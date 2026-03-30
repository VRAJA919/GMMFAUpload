"""GeoManager shell after login: loading overlay, product tile, top navigation, logout."""

from __future__ import annotations

import re

from playwright.sync_api import Frame, Page, TimeoutError as PlaywrightTimeoutError

from config import settings
from pages.base_page import BasePage


class GmShellPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def _administration_entry(self):
        return self.page.get_by_text("Administration").first

    def _shell_ready(self, timeout_ms: int) -> bool:
        try:
            self._administration_entry().wait_for(state="visible", timeout=timeout_ms)
            return True
        except PlaywrightTimeoutError:
            return False

    def _try_click_tile_in_frame(self, frame: Frame) -> bool:
        """Codegen nth-child path often differs on Linux CI vs Windows; try a few patterns per frame."""
        primary = frame.locator(settings.GM_PRODUCT_TILE_SELECTOR).first
        fallbacks = (
            frame.locator("div[tabindex]").filter(
                has_text=re.compile(r"Geo|Manager|Road|Centre", re.I)
            ).first,
            frame.locator("div[tabindex]").nth(0),
            frame.locator("div[tabindex]").nth(1),
        )
        for loc in (primary, *fallbacks):
            try:
                loc.wait_for(state="visible", timeout=12_000)
                loc.click(timeout=45_000, force=True)
                return True
            except Exception:
                continue
        return False

    def finish_login_transition(self) -> None:
        # Prefer exact copy; fallback to anchored regex (broad "GeoManager" regex can match wrong nodes).
        loading = (
            self.page.get_by_text("Loading GeoManager™")
            .or_(self.page.get_by_text(re.compile(r"^\s*Loading\s+GeoManager", re.I)))
            .first
        )
        try:
            loading.wait_for(state="visible", timeout=25_000)
            loading.click(timeout=15_000, force=True)
        except Exception:
            pass

        # GeoManager may already show the top bar on GitHub-hosted runners (no launcher tile needed).
        if self._shell_ready(25_000):
            return

        # Try main document then every frame (Qooxdoo sometimes hosts tiles in nested iframes).
        frames_to_try: list[Frame] = []
        seen: set[int] = set()
        for fr in self.page.frames:
            fid = id(fr)
            if fid not in seen:
                seen.add(fid)
                frames_to_try.append(fr)

        for fr in frames_to_try:
            if self._try_click_tile_in_frame(fr):
                if self._shell_ready(60_000):
                    return

        # Last resort: wait for shell without relying on fragile nth-child selectors.
        self.wait_visible(self._administration_entry(), timeout_ms=120_000)

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
