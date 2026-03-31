"""GeoManager secured login (password step)."""

from __future__ import annotations

import re

from playwright.sync_api import Page, expect

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

    def fill_credentials(self, username: str, password: str) -> None:
        user = self.page.get_by_role("textbox", name="Username")
        pwd = self.page.get_by_role("textbox", name="Password")
        self.wait_visible(user)
        self.wait_visible(pwd)
        user.click()
        user.fill(username)
        user.press("Tab")
        pwd.fill(password)

    def submit(self) -> None:
        self.page.get_by_role("button", name="SIGN IN").click()

    def sign_in(self, username: str, password: str) -> None:
        self.fill_credentials(username, password)
        self.submit()

    def expect_login_form_visible(self, timeout_ms: int | None = None) -> None:
        """Assert secured login page is shown (after logout or deep link)."""
        t = timeout_ms if timeout_ms is not None else self.default_timeout_ms
        expect(self.page).to_have_url(re.compile(r"login\.html"), timeout=t)
        expect(self.page.get_by_role("textbox", name="Username")).to_be_visible(timeout=t)
        expect(self.page.get_by_role("textbox", name="Password")).to_be_visible(timeout=t)
        expect(self.page.get_by_role("button", name="SIGN IN")).to_be_visible(timeout=t)
