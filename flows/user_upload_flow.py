"""Navigate to User Administration upload and process the definition CSV."""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Page

from config import settings
from pages.gm_shell_page import GmShellPage
from pages.gm_user_upload_page import GmUserUploadPage


class UserUploadFlow:
    def __init__(self, page: Page) -> None:
        self._page = page
        self._shell = GmShellPage(page)
        self._upload = GmUserUploadPage(page)

    def upload_user_definition_csv(self, csv_path: Path | None = None) -> None:
        path = csv_path if csv_path is not None else settings.DEFINE_USER_CSV
        path = path.resolve()
        if not path.is_file():
            raise FileNotFoundError(f"CSV not found: {path}")

        self._shell.open_user_administration_from_menu()
        self._upload.open_upload_user_screen()
        self._upload.attach_csv(path)
        self._upload.submit_file_upload()
        self._upload.expect_upload_success_message()
        self._upload.acknowledge_success_and_close()

    def sign_out(self) -> None:
        self._shell.logout()
