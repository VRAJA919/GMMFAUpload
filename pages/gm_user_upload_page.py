"""User definition upload inside the embedded iframe (User Administration)."""

from __future__ import annotations

import re
import time
from pathlib import Path

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from pages.base_page import BasePage


class GmUserUploadPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def _iframe(self):
        return self.page.locator("iframe").content_frame

    def open_upload_user_screen(self) -> None:
        ifr = self._iframe()
        ifr.get_by_role("heading", name="User Administration").click()
        ifr.get_by_role("link", name="Upload User", exact=True).click()
        ifr.get_by_role("heading", name="User Administration").click()

    def attach_csv(self, csv_path: Path) -> None:
        ifr = self._iframe()
        ifr.locator('input[type="file"]').set_input_files(str(csv_path.resolve()))

    def submit_file_upload(self) -> None:
        ifr = self._iframe()

        def _dialog(dialog) -> None:
            try:
                dialog.accept()
            except Exception:
                try:
                    dialog.dismiss()
                except Exception:
                    pass

        self.page.once("dialog", _dialog)
        ifr.get_by_role("button", name="Upload File").click()

    def _try_click_completion_line_anywhere(self) -> None:
        """Some builds show a completion line that must be clicked before Done appears."""
        for frame in self.page.frames:
            for getter in (
                lambda f: f.get_by_text("Upload completed,", exact=True),
                lambda f: f.get_by_text(re.compile(r"Upload\s+completed", re.I)),
                lambda f: f.get_by_text(re.compile(r"upload\s+complete", re.I)),
            ):
                try:
                    getter(frame).first.click(timeout=3000)
                    return
                except PlaywrightTimeoutError:
                    continue

    @staticmethod
    def _try_js_click_done_in_frame(frame) -> bool:
        """Firefox/custom widgets sometimes omit button roles; click via DOM text match."""
        try:
            return bool(
                frame.evaluate(
                    """() => {
                        const labels = [];
                        for (const el of document.querySelectorAll(
                          'button, a, [role="button"], input[type="submit"], input[type="button"]'
                        )) {
                          const t = (el.innerText || el.textContent || el.value || '')
                            .replace(/\\s+/g, ' ').trim();
                          if (/^done$/i.test(t)) {
                            el.click();
                            return true;
                          }
                        }
                        return false;
                    }"""
                )
            )
        except Exception:
            return False

    def _click_done_in_any_frame(self, timeout_ms: int = 180_000) -> None:
        """Done may render in the main document or a nested iframe (not only the first iframe)."""
        deadline = time.monotonic() + timeout_ms / 1000.0
        name_pat = re.compile(r"Done", re.I)
        last_err: Exception | None = None
        while time.monotonic() < deadline:
            if self.page.is_closed():
                raise PlaywrightTimeoutError(
                    "Browser page closed before Done appeared (check for crashes or manual close)."
                )
            for frame in self.page.frames:
                if self._try_js_click_done_in_frame(frame):
                    return
                candidates = (
                    frame.get_by_role("button", name=name_pat).first,
                    frame.get_by_role("link", name=name_pat).first,
                    frame.locator("button").filter(has_text=re.compile(r"^\s*Done\s*$", re.I)).first,
                    frame.get_by_text(re.compile(r"^\s*Done\s*$", re.I)).first,
                    frame.locator("button:has-text('Done')").first,
                    frame.locator("[aria-label*='Done' i]").first,
                    frame.locator("input[type='submit'][value*='Done' i]").first,
                )
                for loc in candidates:
                    try:
                        loc.wait_for(state="visible", timeout=1200)
                        loc.click(timeout=15_000)
                        return
                    except PlaywrightTimeoutError as e:
                        last_err = e
                    except Exception as e:
                        last_err = e
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=500)
            except Exception:
                pass
        raise PlaywrightTimeoutError(f"Done control not found in any frame: {last_err}")

    def expect_upload_success_message(self, timeout_ms: int = 120_000) -> None:
        """
        Assert the iframe shows an upload-completed line after Submit (before Done).
        Isolates upload failures from login/navigation issues.
        """
        deadline = time.monotonic() + timeout_ms / 1000.0
        pat = re.compile(r"Upload\s+completed", re.I)
        last_err: Exception | None = None
        while time.monotonic() < deadline:
            if self.page.is_closed():
                raise AssertionError("Page closed while waiting for upload completion message.")
            for frame in self.page.frames:
                try:
                    loc = frame.get_by_text(pat).first
                    loc.wait_for(state="visible", timeout=800)
                    return
                except PlaywrightTimeoutError as e:
                    last_err = e
                except Exception as e:
                    last_err = e
            time.sleep(0.25)
        raise AssertionError(
            "Upload completion text not found in any frame after submit. "
            "Check CSV validity, permissions, or iframe content. "
            f"Last wait error: {last_err!r}"
        )

    def acknowledge_success_and_close(self) -> None:
        try:
            self.page.wait_for_load_state("networkidle", timeout=45_000)
        except Exception:
            pass
        self._try_click_completion_line_anywhere()
        self._click_done_in_any_frame()
        # Help focus return to main shell; residual dialogs can hide top-bar assertions.
        for _ in range(3):
            try:
                self.page.keyboard.press("Escape")
            except Exception:
                break
