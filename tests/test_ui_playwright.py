"""Playwright UI tests (pytest-playwright), through the LoginPagePW page object.

The first three tests mirror test_ui.py (Selenium) so the two tools can be compared
side by side. The last two use network interception (page.route), which Selenium
can't do natively: the browser's API calls are answered by the test, so the UI's
error handling and data display are tested without changing the backend.
"""
import re

import pytest
from playwright.sync_api import Page, Route, expect

from tests.pages.login_page_pw import LoginPagePW

pytestmark = pytest.mark.playwright


def test_valid_login_shows_welcome(page: Page):
    login = LoginPagePW(page).open().login("operator", "radar123")
    expect(login.welcome).to_have_text("Welcome, operator. 3 active tracks.")
    expect(login.error).to_be_hidden()


def test_invalid_login_shows_error(page: Page):
    login = LoginPagePW(page).open().login("operator", "not-the-password")
    expect(login.error).to_have_text("Invalid username or password")
    expect(login.welcome).to_be_hidden()


def test_page_title(page: Page):
    LoginPagePW(page).open()
    expect(page).to_have_title("Radar Console Login")


def test_backend_outage_shows_server_message(page: Page):
    """Mocked 503 from /api/login: the UI must show the server's message, not crash or hang."""
    page.route("**/api/login", lambda route: route.fulfill(status=503, json={"error": "Service unavailable"}))
    login = LoginPagePW(page).open().login("operator", "radar123")
    expect(login.error).to_have_text("Service unavailable")
    expect(login.welcome).to_be_hidden()


def test_welcome_count_comes_from_tracks_api(page: Page):
    """Mocked /api/tracks with 5 tracks: the welcome line must report 5, proving the count isn't hard-coded."""
    fake_tracks = [{"id": i, "range_m": 100.0 * i, "azimuth_deg": 0.0, "velocity_mps": 0.0,
                    "classification": "drone"} for i in range(1, 6)]
    calls = []

    def handle(route: Route):
        calls.append(route.request.url)
        route.fulfill(json=fake_tracks)

    page.route("**/api/tracks", handle)
    login = LoginPagePW(page).open().login("operator", "radar123")
    expect(login.welcome).to_have_text(re.compile(r"5 active tracks\.$"))
    assert len(calls) == 1, f"expected one /api/tracks call, got {calls}"
