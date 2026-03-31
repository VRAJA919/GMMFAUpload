Refactor the following Playwright codegen script into a Hybrid Framework using:

- Page Object Model (POM)
- Flow layer (business logic)
- Pytest test layer

Rules:
- Extract reusable page methods
- Create flow classes for:
  - Login with MFA
  - User upload
- Remove hardcoded values
- Add clean method names
- Keep code production-ready

Output:
- pages/
- flows/
- tests/

Here is the code:

import re
from playwright.sync_api import Page, expect


def test_example(page: Page) -> None:
    page.goto("https://eugm.road.com/application/signon/secured/login.html")
    page.get_by_role("textbox", name="Username").click()
    page.get_by_role("textbox", name="Username").fill("testvijay")
    page.get_by_role("textbox", name="Username").press("Tab")
    page.get_by_role("textbox", name="Password").fill("Trimble@123")
    page.get_by_role("button", name="SIGN IN").click()
    page.get_by_text("Loading GeoManager™").click()
    page.locator("div:nth-child(4) > div > div > div > div:nth-child(2) > div > div > div > div > div > div > div > div > div > div:nth-child(3) > div").first.click()
    page.get_by_text("Administration").click()
    page.get_by_text("User", exact=True).click()
    page.get_by_text("User Administration").nth(1).click()
    page.locator("iframe").content_frame.get_by_role("heading", name="User Administration").click()
    page.locator("iframe").content_frame.get_by_role("link", name="Upload User", exact=True).click()
    page.locator("iframe").content_frame.get_by_role("heading", name="User Administration").click()
    page.locator("iframe").content_frame.get_by_role("button", name="Choose File").click()
    page.locator("iframe").content_frame.get_by_role("button", name="Choose File").set_input_files("define_user (1).csv")
    page.once("dialog", lambda dialog: dialog.dismiss())
    page.locator("iframe").content_frame.get_by_role("button", name="Upload File").click()
    page.locator("iframe").content_frame.get_by_text("Upload completed,").click()
    page.locator("iframe").content_frame.get_by_role("button", name="Done").click()
    page.get_by_text("Logout").click()
