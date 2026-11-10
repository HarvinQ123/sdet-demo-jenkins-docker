"""Selenium UI tests, written through the LoginPage page object."""
import pytest

from tests.pages.login_page import LoginPage

pytestmark = pytest.mark.ui


def test_valid_login_shows_welcome(driver, base_url):
    page = LoginPage(driver, base_url).open()
    page.login("operator", "radar123")
    assert page.welcome_text() == "Welcome, operator. 3 active tracks."


def test_invalid_login_shows_error(driver, base_url):
    page = LoginPage(driver, base_url).open()
    page.login("operator", "not-the-password")
    assert page.error_text() == "Invalid username or password"


def test_page_title(driver, base_url):
    LoginPage(driver, base_url).open()
    assert driver.title == "Radar Console Login"
