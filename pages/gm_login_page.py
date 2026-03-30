"""GeoManager secured login (password step)."""

from __future__ import annotations

from playwright.sync_api import Page

from config import settings
from pages.base_page import BasePage


class GmLoginPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def open(self) -> None:
        self.page.goto(
            settings.GM_LOGIN_URL,
            wait_until="domcontentloaded",
            timeout=settings.NAVIGATION_TIMEOUT_MS,
        )

    def sign_in(self, username: str, password: str) -> None:
        user = self.page.get_by_role("textbox", name="Username")
        pwd = self.page.get_by_role("textbox", name="Password")
        self.wait_visible(user)
        self.wait_visible(pwd)
        user.click()
        user.fill(username)
        user.press("Tab")
        pwd.fill(password)
        self.page.get_by_role("button", name="SIGN IN").click()
