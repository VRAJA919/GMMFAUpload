"""Pytest / Playwright defaults, Allure failure screenshots (same pattern as GMloginMFA)."""

from __future__ import annotations

from pathlib import Path

import allure
import pytest

_ARTIFACTS = Path(__file__).resolve().parent / "artifacts"
_ALLURE = Path(__file__).resolve().parent / "allure-results"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    outcome = yield
    rep = outcome.get_result()
    if rep.when != "call" or not rep.failed:
        return
    page = item.funcargs.get("page")
    if page is None:
        return
    try:
        png = page.screenshot(full_page=True)
        allure.attach(
            png,
            name="failure_screenshot",
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception:
        pass


def pytest_sessionstart(session: pytest.Session) -> None:
    _ALLURE.mkdir(parents=True, exist_ok=True)
    _ARTIFACTS.mkdir(parents=True, exist_ok=True)
