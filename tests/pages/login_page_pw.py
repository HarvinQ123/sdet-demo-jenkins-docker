"""Playwright page object for the Radar Console login page.

Same job as login_page.py (Selenium), different tool. Compare the two:
  * Locators are user-facing (label text, button role), not raw IDs, so tests
    read like what a person does and survive markup changes.
  * There are no explicit waits here. Playwright auto-waits for an element to be
    visible and enabled before acting, and `expect(...)` assertions retry until
    they pass or time out. The random 300-1800 ms delay in the app needs no code.
"""
from playwright.sync_api import Page


class LoginPagePW:
    def __init__(self, page: Page):
        self.page = page
        self.username = page.get_by_label("Username")
        self.password = page.get_by_label("Password")
        self.submit = page.get_by_role("button", name="Sign in")
        self.welcome = page.locator("#welcome")
        self.error = page.locator("#error")

    def open(self):
        self.page.goto("/login")  # relative: pytest-playwright sets the context's base_url from our fixture
        return self

    def login(self, username, password):
        self.username.fill(username)
        self.password.fill(password)
        self.submit.click()
        return self
