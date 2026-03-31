"""Retry utilities with bounded jitter between OTP polls."""

from __future__ import annotations

import random
import time

from utils.logger import get_logger

logger = get_logger(__name__)


def sleep_between_otp_attempts(min_sec: float, max_sec: float) -> None:
    """Bounded wait between OTP polls (3–5s style)."""
    time.sleep(random.uniform(min_sec, max_sec))
