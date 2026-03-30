"""Email / OTP step after password (optional per environment)."""

from __future__ import annotations

import re

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from pages.base_page import BasePage
from utils.exceptions import MFAStateError


class GmMFAPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def _otp_locator(self):
        return (
            self.page.locator("#emailOtpInput")
            .or_(self.page.locator("input[name='emailOtp']"))
            .or_(self.page.get_by_placeholder("Code", exact=True))
            .or_(
                self.page.locator(
                    "input[autocomplete='one-time-code'], "
                    "input[inputmode='numeric'], input[name='code'], input[name='otp']"
                )
            )
            .first
        )

    def is_mfa_visible(self, timeout_ms: int = 5000) -> bool:
        try:
            self._otp_locator().wait_for(state="visible", timeout=timeout_ms)
            return True
        except PlaywrightTimeoutError:
            return False

    def enter_and_submit_otp(self, code: str) -> None:
        if len(code) != 6 or not code.isdigit():
            raise MFAStateError("OTP must be 6 digits")
        loc = self._otp_locator()
        loc.wait_for(state="visible", timeout=self.default_timeout_ms)
        loc.fill(code)
        for sel in (
            "button[type='submit']",
            "button:has-text('VERIFY')",
            "button:has-text('Verify')",
            "button:has-text('CONTINUE')",
        ):
            btn = self.page.locator(sel).first
            if btn.count() > 0 and btn.is_enabled():
                btn.click()
                return
        raise MFAStateError("No MFA submit control found")
