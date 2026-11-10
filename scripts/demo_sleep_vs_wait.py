"""Show, with numbers, why time.sleep() is the wrong way to wait in Selenium.

Logs in N times with each strategy and prints pass count and total time:
  sleep : click, time.sleep(1), then check   (the page takes 0.3-1.8 s at random)
  wait  : click, WebDriverWait until visible  (returns the moment it appears)

Run from the project root:  .venv/bin/python scripts/demo_sleep_vs_wait.py
"""
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium.common.exceptions import TimeoutException  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402

from app.radar_app import make_server  # noqa: E402
from tests.conftest import make_driver  # noqa: E402

RUNS = 10


def log_in(driver, base_url):
    driver.get(f"{base_url}/login")
    driver.find_element(By.ID, "username").send_keys("operator")
    driver.find_element(By.ID, "password").send_keys("radar123")
    driver.find_element(By.ID, "login-btn").click()


def with_sleep(driver, base_url):
    log_in(driver, base_url)
    time.sleep(1)  # guess how long the page needs
    return driver.find_element(By.ID, "welcome").is_displayed()


def with_wait(driver, base_url):
    log_in(driver, base_url)
    try:
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "welcome")))
        return True
    except TimeoutException:
        return False


def main():
    server = make_server()
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    driver = make_driver()
    try:
        for name, strategy in [("time.sleep(1)", with_sleep), ("WebDriverWait", with_wait)]:
            start = time.perf_counter()
            passed = sum(strategy(driver, base_url) for _ in range(RUNS))
            elapsed = time.perf_counter() - start
            print(f"{name:<14} passed {passed:>2}/{RUNS}   total {elapsed:5.1f} s")
    finally:
        driver.quit()
        server.shutdown()


if __name__ == "__main__":
    main()
