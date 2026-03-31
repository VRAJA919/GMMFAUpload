"""E2E: split scenarios for clear failure attribution (login / upload / logout)."""

from __future__ import annotations

import allure
import pytest
from playwright.sync_api import Page

from flows.login_flow import LoginFlow
from flows.user_upload_flow import UserUploadFlow
from pages.gm_login_page import GmLoginPage
from pages.gm_shell_page import GmShellPage


@allure.epic("GeoManager PROD")
@allure.feature("User definition file upload")
@pytest.mark.e2e
class TestGeoManagerUserUploadE2E:
    """
    One shared browser session (class-scoped ``gm_page``): MFA runs once; failures map to a single step.

    Order: ``test_01`` → ``test_02`` → ``test_03`` (lexical). If ``test_01`` fails, later tests may be invalid.
    """

    @allure.story("Authentication")
    @allure.title("1. Login with MFA — shell ready")
    @allure.description(
        "Secured login, email OTP when shown, then GeoManager shell (Administration visible). "
        "Fails here: credentials, MFA/Mailinator, or post-login shell."
    )
    def test_01_login_with_mfa(self, gm_page: Page) -> None:
        LoginFlow(gm_page).authenticate()
        GmShellPage(gm_page).expect_authenticated_shell()

    @allure.story("User Administration")
    @allure.title("2. Upload user definition CSV — success acknowledged")
    @allure.description(
        "Navigate to User Administration → Upload User, attach CSV, assert completion text, Done. "
        "Fails here: navigation, iframe, file, or server-side validation — not login."
    )
    def test_02_upload_verification(self, gm_page: Page) -> None:
        UserUploadFlow(gm_page).upload_user_definition_csv()
        # URL-only: top-bar locators often match hidden duplicates after iframe/modal upload UI.
        GmShellPage(gm_page).expect_still_logged_in()

    @allure.story("Session")
    @allure.title("3. Logout — login form visible")
    @allure.description(
        "Logout from shell; assert secured login page. Fails here: logout control or redirect."
    )
    def test_03_logout(self, gm_page: Page) -> None:
        UserUploadFlow(gm_page).sign_out()
        GmLoginPage(gm_page).expect_login_form_visible()
