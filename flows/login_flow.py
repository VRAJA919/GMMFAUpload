"""Password sign-in plus MFA (static OTP or Mailinator/IMAP like GMloginMFA), then shell."""

from __future__ import annotations

import os

from playwright.sync_api import Page

from config import settings
from pages.gm_login_page import GmLoginPage
from pages.gm_mfa_page import GmMFAPage
from pages.gm_shell_page import GmShellPage
from utils.email_helper import (
    mailinator_existing_message_ids,
    otp_retrieval_configured,
    wait_for_otp,
)


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

        if not user or not pwd:
            raise RuntimeError(
                "Set GM_USERNAME and GM_PASSWORD in .env (or pass username= / password=)."
            )

        inbox = settings.otp_mailinator_inbox()
        use_dynamic_otp = (
            otp is None
            and inbox is not None
            and otp_retrieval_configured()
        )

        self._login.open()

        mail_ids_before: set[str] | None = None
        if use_dynamic_otp:
            mail_ids_before = mailinator_existing_message_ids(inbox)
            self._login.fill_credentials(user, pwd)
            self._login.submit()
        else:
            self._login.sign_in(user, pwd)

        # Do not wait for networkidle here — it can dismiss the "Loading GeoManager" overlay
        # before finish_login_transition() needs to click it.

        mfa_wait_ms = 22_000 if os.getenv("CI") else 8_000
        if self._mfa.is_mfa_visible(timeout_ms=mfa_wait_ms):
            if not otp:
                if not use_dynamic_otp:
                    raise RuntimeError(
                        "MFA is required: set GM_OTP_CODE, or GM_OTP_EMAIL (or OTP_EMAIL) with "
                        "MAILINATOR_DOMAIN=public (or MAILINATOR_API_TOKEN / IMAP_*), "
                        "or pass otp_code= to LoginFlow.authenticate(). "
                        "In GitHub Actions, add repository secrets GM_OTP_EMAIL or OTP_EMAIL "
                        "(or GM_OTP_CODE / IMAP_*); see README CI/CD."
                    )
                assert inbox is not None
                otp = wait_for_otp(
                    inbox,
                    exclude_message_ids=mail_ids_before or set(),
                )
            self._mfa.enter_and_submit_otp(otp)

        self._shell.finish_login_transition()
