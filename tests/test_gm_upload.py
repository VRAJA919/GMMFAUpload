"""E2E: hybrid flow (login + optional MFA + user definition upload)."""

import pytest
from playwright.sync_api import Page

from config import settings
from flows.login_flow import LoginFlow
from flows.user_upload_flow import UserUploadFlow


@pytest.mark.e2e
def test_example(page: Page) -> None:
    page.set_default_timeout(settings.DEFAULT_TIMEOUT_MS)
    LoginFlow(page).authenticate()
    upload = UserUploadFlow(page)
    upload.upload_user_definition_csv()
    upload.sign_out()
