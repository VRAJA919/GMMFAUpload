"""Shared page primitives."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from config import settings


class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.default_timeout_ms = settings.DEFAULT_TIMEOUT_MS

    def wait_visible(self, locator: Locator, timeout_ms: int | None = None) -> Locator:
        t = timeout_ms if timeout_ms is not None else self.default_timeout_ms
        locator.wait_for(state="visible", timeout=t)
        return locator
