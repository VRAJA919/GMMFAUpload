"""OTP retrieval: Mailinator API (preferred), IMAP fallback (same pattern as GMloginMFA)."""

from __future__ import annotations

import email as py_email
import imaplib
import re
from typing import Any

import requests

from config import settings
from utils.exceptions import OTPNotFoundError
from utils.logger import get_logger
from utils.retry_helper import sleep_between_otp_attempts

logger = get_logger(__name__)

OTP_PATTERN = re.compile(r"\b(\d{6})\b")

_GEO_VERIFICATION_PATTERNS = [
    re.compile(
        r"(?is)verification\s+code\s+you\s+requested\s+is[:\s]+(\d{6})\b",
    ),
    re.compile(
        r"(?is)GeoManager\s+verification\s+code[^0-9]{0,120}(\d{6})\b",
    ),
    re.compile(
        r"(?is)(?:one[- ]?time\s+code|verification\s+code)\s*[:is]+\s*(\d{6})\b",
    ),
]


def mailinator_api_available() -> bool:
    """
    Public @mailinator.com inboxes use domain ``public`` on the v2 API with no token.
    """
    if settings.MAILINATOR_API_TOKEN.strip():
        return True
    return settings.MAILINATOR_DOMAIN.lower().strip() == "public"


def extract_otp_from_text(text: str) -> str | None:
    """Extract a 6-digit OTP; avoid mistaking CSS hex colors for codes."""
    if not text:
        return None
    for pat in _GEO_VERIFICATION_PATTERNS:
        m = pat.search(text)
        if m:
            return m.group(1)
    cleaned = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", text)
    cleaned = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", cleaned)
    cleaned = re.sub(r"#([0-9a-fA-F]{6})\b", " ", cleaned)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    matches = OTP_PATTERN.findall(cleaned)
    if not matches:
        return None
    return matches[-1]


def _mailinator_headers() -> dict[str, str]:
    h: dict[str, str] = {"Accept": "application/json"}
    if settings.MAILINATOR_API_TOKEN:
        h["Authorization"] = f"Bearer {settings.MAILINATOR_API_TOKEN}"
    return h


def mailinator_existing_message_ids(inbox: str) -> set[str]:
    """IDs already in the inbox (used to ignore pre-login messages)."""
    ids: set[str] = set()
    for m in _list_mailinator_messages(inbox):
        mid = m.get("id") or m.get("messageId")
        if mid:
            ids.add(str(mid))
    return ids


def _list_mailinator_messages(inbox: str) -> list[dict[str, Any]]:
    url = (
        f"{settings.MAILINATOR_API_BASE.rstrip('/')}/domains/"
        f"{settings.MAILINATOR_DOMAIN}/inboxes/{inbox}"
    )
    r = requests.get(url, headers=_mailinator_headers(), timeout=30)
    r.raise_for_status()
    data = r.json()
    msgs = data.get("msgs") or data.get("messages") or []
    if not isinstance(msgs, list):
        return []
    return msgs


def _get_mailinator_message_raw(inbox: str, message_id: str) -> str:
    url = (
        f"{settings.MAILINATOR_API_BASE.rstrip('/')}/domains/"
        f"{settings.MAILINATOR_DOMAIN}/inboxes/{inbox}/messages/{message_id}"
    )
    r = requests.get(url, headers=_mailinator_headers(), timeout=30)
    r.raise_for_status()
    payload = r.json()
    if not isinstance(payload, dict):
        return str(payload)
    parts = payload.get("parts") or []
    chunks: list[str] = []
    subj = payload.get("subject")
    if isinstance(subj, str):
        chunks.append(subj)
    for p in parts:
        body = p.get("body")
        if isinstance(body, str):
            chunks.append(body)
    if not chunks and isinstance(payload.get("text"), str):
        chunks.append(payload["text"])
    return "\n".join(chunks) if chunks else str(payload)


def fetch_otp_from_mailinator(
    inbox: str,
    min_message_time_ms: int | None = None,
    exclude_message_ids: set[str] | None = None,
) -> str:
    """Fetch latest messages and return first 6-digit OTP found."""
    messages = _list_mailinator_messages(inbox)
    messages.sort(key=lambda m: m.get("time", 0), reverse=True)
    excluded = exclude_message_ids or set()
    for msg in messages[:15]:
        mid = msg.get("id") or msg.get("messageId")
        if not mid:
            continue
        if str(mid) in excluded:
            continue
        if min_message_time_ms is not None:
            mt = msg.get("time")
            if isinstance(mt, (int, float)) and int(mt) < min_message_time_ms:
                continue
        subj = msg.get("subject") or ""
        otp = extract_otp_from_text(subj)
        if otp:
            logger.info("OTP extracted from Mailinator list subject %s", mid)
            return otp
        try:
            raw = _get_mailinator_message_raw(inbox, str(mid))
        except requests.RequestException as exc:
            logger.debug("Skip message %s: %s", mid, exc)
            continue
        otp = extract_otp_from_text(raw)
        if otp:
            logger.info("OTP extracted from Mailinator message %s", mid)
            return otp
    raise OTPNotFoundError("No 6-digit OTP found in recent Mailinator messages")


def fetch_otp_from_imap() -> str:
    """IMAP fallback using configured mailbox."""
    if not settings.IMAP_HOST or not settings.IMAP_USER:
        raise OTPNotFoundError("IMAP not configured (IMAP_HOST / IMAP_USER)")
    client = imaplib.IMAP4_SSL(settings.IMAP_HOST, settings.IMAP_PORT)
    try:
        client.login(settings.IMAP_USER, settings.IMAP_PASSWORD)
        client.select(settings.IMAP_MAILBOX)
        typ, data = client.search(None, "ALL")
        if typ != "OK" or not data or not data[0]:
            raise OTPNotFoundError("No IMAP messages")
        ids = data[0].split()
        for msg_id in reversed(ids[-20:]):
            typ, msg_data = client.fetch(msg_id, "(RFC822)")
            if typ != "OK" or not msg_data or not msg_data[0]:
                continue
            raw_email = msg_data[0][1]
            msg = py_email.message_from_bytes(raw_email)
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body += part.get_payload(decode=True).decode(
                            errors="ignore"
                        )
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")
            otp = extract_otp_from_text(body)
            if otp:
                return otp
    finally:
        try:
            client.logout()
        except Exception:
            pass
    raise OTPNotFoundError("No 6-digit OTP found via IMAP")


def wait_for_otp(
    inbox: str,
    min_message_time_ms: int | None = None,
    exclude_message_ids: set[str] | None = None,
) -> str:
    """Poll Mailinator (then IMAP) with retries."""
    last: Exception | None = None
    for attempt in range(1, settings.OTP_MAX_ATTEMPTS + 1):
        if mailinator_api_available():
            try:
                return fetch_otp_from_mailinator(
                    inbox,
                    min_message_time_ms=min_message_time_ms,
                    exclude_message_ids=exclude_message_ids,
                )
            except (requests.RequestException, OTPNotFoundError) as e:
                last = e
                logger.info(
                    "Mailinator attempt %s/%s: %s",
                    attempt,
                    settings.OTP_MAX_ATTEMPTS,
                    e,
                )
        if settings.IMAP_HOST and settings.IMAP_USER:
            try:
                return fetch_otp_from_imap()
            except OTPNotFoundError as e:
                last = e
                logger.info(
                    "IMAP attempt %s/%s: %s", attempt, settings.OTP_MAX_ATTEMPTS, e
                )
        if attempt < settings.OTP_MAX_ATTEMPTS:
            sleep_between_otp_attempts(
                settings.OTP_RETRY_MIN_SEC, settings.OTP_RETRY_MAX_SEC
            )
    if not mailinator_api_available() and not (
        settings.IMAP_HOST and settings.IMAP_USER
    ):
        raise OTPNotFoundError(
            "Use MAILINATOR_DOMAIN=public for @mailinator.com inboxes, "
            "or set MAILINATOR_API_TOKEN (private domain), or IMAP_* for OTP."
        )
    raise OTPNotFoundError(
        f"OTP not found after {settings.OTP_MAX_ATTEMPTS} attempts: {last}"
    )


def otp_retrieval_configured() -> bool:
    """True if Mailinator public/token or IMAP can be used to fetch an OTP."""
    return mailinator_api_available() or bool(
        settings.IMAP_HOST and settings.IMAP_USER
    )
