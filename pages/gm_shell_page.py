"""GeoManager shell after login: loading overlay, product tile, top navigation, logout."""

from __future__ import annotations

import re
import time

from playwright.sync_api import Frame, Page, TimeoutError as PlaywrightTimeoutError, expect

from config import settings
from pages.base_page import BasePage


class GmShellPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def _administration_entry(self):
        # Substring match would hit hidden headings like "Welcome to GeoManager Administration."
        return self.page.get_by_text("Administration", exact=True).first

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
        adm = self.page.get_by_text("Administration", exact=True)
        self.wait_visible(adm)
        adm.click()
        self.wait_visible(self.page.get_by_text("User", exact=True))
        self.page.get_by_text("User", exact=True).click()
        ua = self.page.get_by_text("User Administration").nth(1)
        self.wait_visible(ua)
        ua.click()

    def logout(self) -> None:
        self.wait_visible(self.page.get_by_text("Logout"))
        self.page.get_by_text("Logout").click()

    def expect_still_logged_in(self, timeout_ms: int | None = None) -> None:
        """
        Assert the session is still active (not redirected to secured login).
        Use after heavy iframe/modal flows where top-bar locators can match hidden duplicates.
        """
        t = timeout_ms if timeout_ms is not None else self.default_timeout_ms
        expect(self.page).not_to_have_url(re.compile(r"login\.html"), timeout=t)

    def expect_authenticated_shell(self, timeout_ms: int | None = None) -> None:
        """
        Assert user is past login and the shell is usable.

        Scans **every frame** for a visible ``Logout`` or exact ``Administration`` (Qooxdoo may
        host the top bar in the main document or a child frame; substring matches are avoided).
        Dismisses stray overlays with Escape while polling.
        """
        t = timeout_ms if timeout_ms is not None else self.default_timeout_ms
        expect(self.page).not_to_have_url(re.compile(r"login\.html"), timeout=t)
        deadline = time.monotonic() + t / 1000.0
        last_err: Exception | None = None
        esc_every = 0
        while time.monotonic() < deadline:
            if esc_every % 8 == 0:
                try:
                    self.page.keyboard.press("Escape")
                except Exception:
                    pass
            esc_every += 1
            for frame in self.page.frames:
                for loc in (
                    frame.get_by_text("Logout").first,
                    frame.get_by_text("Administration", exact=True).first,
                ):
                    try:
                        loc.wait_for(state="visible", timeout=600)
                        return
                    except PlaywrightTimeoutError as e:
                        last_err = e
                    except Exception as e:
                        last_err = e
            time.sleep(0.15)
        raise AssertionError(
            "Authenticated shell not detected: no visible Logout or exact 'Administration' "
            f"in any frame within {t} ms. Last error: {last_err!r}"
        )
