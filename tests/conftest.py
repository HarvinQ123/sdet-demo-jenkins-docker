"""Shared pytest fixtures: the app under test, an HTTP session, and a Chrome driver."""
import os
import shutil
import threading
from pathlib import Path

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from app.radar_app import make_server

REPORTS = Path(__file__).resolve().parent.parent / "reports"


@pytest.fixture(scope="session")
def base_url():
    """Start the radar app on a free port for the whole test session."""
    server = make_server()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()


@pytest.fixture
def api(base_url):
    """requests.Session with the base URL baked in: api.get('/api/health')."""
    session = requests.Session()
    session.request = _with_base(session.request, base_url)
    yield session
    session.close()


def _with_base(request, base_url):
    def wrapped(method, path, **kwargs):
        kwargs.setdefault("timeout", 5)
        return request(method, base_url + path, **kwargs)
    return wrapped


def make_driver():
    """Chrome, headless unless HEADED=1 is set.

    Inside the Jenkins container, Chromium and chromedriver come from apt.
    On a Mac with Google Chrome, Selenium Manager downloads the matching driver.
    SELENIUM_MANAGER=1 forces Selenium Manager even when chromium is on PATH
    (GitHub Actions runners have both, and their versions can disagree).
    """
    options = webdriver.ChromeOptions()
    if os.environ.get("HEADED") != "1":
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,800")  # headless defaults to a small window
    options.add_argument("--no-sandbox")             # needed when Chrome runs in a container
    options.add_argument("--disable-dev-shm-usage")  # container /dev/shm is tiny

    use_path = os.environ.get("SELENIUM_MANAGER") != "1"
    chromium = shutil.which("chromium") if use_path else None
    if chromium:
        options.binary_location = chromium
    driver_path = shutil.which("chromedriver") if use_path else None
    service = Service(executable_path=driver_path) if driver_path else Service()
    return webdriver.Chrome(options=options, service=service)


@pytest.fixture
def driver():
    drv = make_driver()
    yield drv
    drv.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """On a UI test failure, save a screenshot to reports/screenshots/ (Jenkins archives it)."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed and "driver" in item.fixturenames:
        shots = REPORTS / "screenshots"
        shots.mkdir(parents=True, exist_ok=True)
        item.funcargs["driver"].save_screenshot(str(shots / f"{item.name}.png"))
