"""Environment-driven settings (no hardcoded secrets in tests)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")

DEFAULT_TIMEOUT_MS = int(os.getenv("PLAYWRIGHT_TIMEOUT_MS", "90000"))
NAVIGATION_TIMEOUT_MS = int(os.getenv("PLAYWRIGHT_NAVIGATION_TIMEOUT_MS", "90000"))

GM_LOGIN_URL = os.getenv(
    "GM_LOGIN_URL",
    "https://eugm.road.com/application/signon/secured/login.html",
)
GM_USERNAME = os.getenv("GM_USERNAME", "").strip()
GM_PASSWORD = os.getenv("GM_PASSWORD", "").strip()
# Static OTP (CI one-shot). Prefer unset + GM_OTP_EMAIL for Mailinator/IMAP fetch.
GM_OTP_CODE = os.getenv("GM_OTP_CODE", "").strip() or None

# OTP polling / Mailinator / IMAP (aligned with GMloginMFA)
OTP_MAX_ATTEMPTS = int(os.getenv("OTP_MAX_ATTEMPTS", "15"))
OTP_RETRY_MIN_SEC = float(os.getenv("OTP_RETRY_MIN_SEC", "3"))
OTP_RETRY_MAX_SEC = float(os.getenv("OTP_RETRY_MAX_SEC", "5"))
MAILINATOR_DOMAIN = os.getenv("MAILINATOR_DOMAIN", "public")
MAILINATOR_API_TOKEN = os.getenv("MAILINATOR_API_TOKEN", "")
MAILINATOR_API_BASE = os.getenv(
    "MAILINATOR_API_BASE", "https://api.mailinator.com/v2"
)
IMAP_HOST = os.getenv("IMAP_HOST", "")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
IMAP_USER = os.getenv("IMAP_USER", "")
IMAP_PASSWORD = os.getenv("IMAP_PASSWORD", "")
IMAP_MAILBOX = os.getenv("IMAP_MAILBOX", "INBOX")


def otp_mailinator_inbox() -> str | None:
    """Local-part of inbox for Mailinator (full email or local-part in GM_OTP_EMAIL / OTP_EMAIL)."""
    raw = (
        os.getenv("GM_OTP_EMAIL", "").strip() or os.getenv("OTP_EMAIL", "").strip()
    )
    if not raw:
        return None
    if "@" in raw:
        return raw.split("@", 1)[0]
    return raw

_csv = os.getenv("GM_UPLOAD_CSV", "").strip()
if _csv:
    _p = Path(_csv)
    DEFINE_USER_CSV = _p.resolve() if _p.is_absolute() else (_ROOT / _p).resolve()
else:
    DEFINE_USER_CSV = (_ROOT / "define_user (1).csv").resolve()

# Fragile codegen selector; override via env if the shell layout changes.
GM_PRODUCT_TILE_SELECTOR = os.getenv(
    "GM_PRODUCT_TILE_SELECTOR",
    "div:nth-child(4) > div > div > div > div:nth-child(2) > div > div > div > div > div > div > div > div > div > div:nth-child(3) > div",
)
