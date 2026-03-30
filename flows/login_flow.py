"""Password sign-in plus optional MFA, then shell transition."""

from __future__ import annotations

from playwright.sync_api import Page

from config import settings
from pages.gm_login_page import GmLoginPage
from pages.gm_mfa_page import GmMFAPage
from pages.gm_shell_page import GmShellPage


class LoginFlow:
    def __init__(self, page: Page) -> None:
        self._page = page
        self._login = GmLoginPage(page)
        self._mfa = GmMFAPage(page)
        self._shell = GmShellPage(page)

    def authenticate(
        self,
        username: str | None = None,
        password: str | None = None,
        *,
        otp_code: str | None = None,
    ) -> None:
        user = username if username is not None else settings.GM_USERNAME
        pwd = password if password is not None else settings.GM_PASSWORD
        otp = otp_code if otp_code is not None else settings.GM_OTP_CODE

        self._login.open()
        self._login.sign_in(user, pwd)

        if self._mfa.is_mfa_visible():
            if not otp:
                raise RuntimeError(
                    "MFA is required for this account; set GM_OTP_CODE in .env "
                    "or pass otp_code= to LoginFlow.authenticate()."
                )
            self._mfa.enter_and_submit_otp(otp)

        self._shell.finish_login_transition()
