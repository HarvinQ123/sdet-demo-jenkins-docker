"""Page object for the Radar Console login page.

Tests talk to this class ("log in as operator"), never to raw locators.
If the page's HTML changes, only this file changes.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class LoginPage:
    # Locators: kept in ONE place
    USERNAME = (By.ID, "username")
    PASSWORD = (By.ID, "password")
    SUBMIT = (By.ID, "login-btn")
    WELCOME = (By.ID, "welcome")
    ERROR = (By.ID, "error")

    def __init__(self, driver, base_url, timeout=5):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, timeout)

    def open(self):
        self.driver.get(f"{self.base_url}/login")
        self.wait.until(EC.visibility_of_element_located(self.USERNAME))
        return self

    def login(self, username, password):
        self.driver.find_element(*self.USERNAME).clear()
        self.driver.find_element(*self.USERNAME).send_keys(username)
        self.driver.find_element(*self.PASSWORD).clear()
        self.driver.find_element(*self.PASSWORD).send_keys(password)
        self.driver.find_element(*self.SUBMIT).click()
        return self

    # Explicit waits: poll until the condition is true, up to `timeout` seconds,
    # and return as soon as it is. No time.sleep anywhere.
    def welcome_text(self):
        return self.wait.until(EC.visibility_of_element_located(self.WELCOME)).text

    def error_text(self):
        return self.wait.until(EC.visibility_of_element_located(self.ERROR)).text
