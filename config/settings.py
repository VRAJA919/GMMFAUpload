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
GM_USERNAME = os.getenv("GM_USERNAME", "testvijay")
GM_PASSWORD = os.getenv("GM_PASSWORD", "Trimble@123")
# When the app shows email OTP after password, set this (or pass into the flow).
GM_OTP_CODE = os.getenv("GM_OTP_CODE", "").strip() or None

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
