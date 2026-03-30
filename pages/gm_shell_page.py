"""GeoManager shell after login: loading overlay, product tile, top navigation, logout."""

from __future__ import annotations

from playwright.sync_api import Page

from config import settings
from pages.base_page import BasePage


class GmShellPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def finish_login_transition(self) -> None:
        self.page.get_by_text("Loading GeoManager™").click()
        self.page.locator(settings.GM_PRODUCT_TILE_SELECTOR).first.click()

    def open_user_administration_from_menu(self) -> None:
        self.wait_visible(self.page.get_by_text("Administration"))
        self.page.get_by_text("Administration").click()
        self.wait_visible(self.page.get_by_text("User", exact=True))
        self.page.get_by_text("User", exact=True).click()
        ua = self.page.get_by_text("User Administration").nth(1)
        self.wait_visible(ua)
        ua.click()

    def logout(self) -> None:
        self.wait_visible(self.page.get_by_text("Logout"))
        self.page.get_by_text("Logout").click()
