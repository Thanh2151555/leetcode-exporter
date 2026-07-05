import logging
import time
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.exceptions import LoginFailedException


logger = logging.getLogger("leetcode_exporter")


class LoginService:
    def __init__(self, driver: Chrome, username: str = "", password: str = "") -> None:
        self.driver = driver
        self.username = username
        self.password = password

    def _is_logged_in(self) -> bool:
        self.driver.get("https://leetcode.com/")
        try:
            # Wait for either the login link or the Premium button to ensure page has loaded
            WebDriverWait(self.driver, 10).until(
                lambda d: len(d.find_elements(By.XPATH, "//a[contains(@href, '/accounts/login')]")) > 0 or 
                          "Sign in" in d.page_source or "Premium" in d.page_source or "Log in" in d.page_source
            )
            
            # If a visible login link exists, we are not logged in
            login_link = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/accounts/login')]")
            if login_link and any(link.is_displayed() for link in login_link):
                return False
                
            # Otherwise, assume we are logged in
            return True
        except TimeoutException:
            logger.debug("Timeout waiting for page to load during login check.")
            return False

    def _is_google_logged_in(self) -> bool:
        try:
            url = self.driver.current_url.lower()
            if "mail.google.com" in url and "signin" not in url:
                return True
            if "accounts.google.com" in url and "signin" not in url:
                return True
            return False
        except Exception:
            return False

    def _find_element(self, xpaths: list[str], timeout: int = 15):
        for xpath in xpaths:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                if element:
                    return element
            except Exception:
                continue
        return None

    def _login_with_credentials(self) -> bool:
        if not self.username or not self.password:
            return False

        try:
            logger.info("Attempting LeetCode login with provided credentials.")
            email_selectors = [
                "//input[@name='login']",
                "//input[@id='id_login']",
                "//input[@type='email']",
                "//input[@type='text' and (contains(@autocomplete, 'email') or contains(@placeholder, 'Email') or contains(@placeholder, 'Username'))]",
            ]
            password_selectors = [
                "//input[@name='password']",
                "//input[@id='id_password']",
                "//input[@type='password']",
            ]

            email_input = self._find_element(email_selectors)
            password_input = self._find_element(password_selectors)

            if not email_input or not password_input:
                logger.debug("Could not find login form fields on LeetCode login page.")
                return False

            email_input.clear()
            email_input.send_keys(self.username)
            password_input.clear()
            password_input.send_keys(self.password)

            submit_buttons = self.driver.find_elements(
                By.XPATH,
                "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sign in') or contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'log in')]")
            for button in submit_buttons:
                try:
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        return True
                except Exception:
                    continue

            password_input.send_keys(Keys.RETURN)
            return True
        except Exception as exc:
            logger.debug("Credential login attempt failed: %s", exc, exc_info=True)

        return False

    def _click_google_button(self) -> bool:
        try:
            logger.info("Trying to click the Google sign-in button on LeetCode login page.")
            button_selectors = [
                "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'google')]",
                "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'google')]",
                "//div[contains(@class, 'google') and (contains(., 'Google') or contains(., 'google'))]",
            ]
            for selector in button_selectors:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    try:
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            return True
                    except Exception:
                        continue
        except Exception:
            pass
        return False

    def _wait_for_condition(self, condition, timeout: int) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(condition)
            return True
        except Exception:
            return False

    def ensure_login(self, timeout: int = 120) -> None:
        self.driver.get("https://leetcode.com/accounts/login/")

        if self._is_logged_in():
            logger.info("Already logged in to LeetCode.")
            return

        if self._login_with_credentials():
            logger.info("Credentials submitted; waiting for login completion.")
            if self._wait_for_condition(lambda d: self._is_logged_in(), timeout):
                logger.info("Login detected after credential submission.")
                return
            logger.info("Credential login did not complete automatically; continuing with fallback.")

        if self._click_google_button():
            logger.info("Google sign-in clicked; waiting for login completion.")
            if self._wait_for_condition(lambda d: self._is_logged_in() or "leetcode.com/problemset" in d.current_url.lower(), timeout):
                logger.info("Login detected after Google sign-in.")
                return
            logger.info("Google sign-in did not complete automatically; opening Gmail for manual login.")

        logger.info("Not logged in to LeetCode yet; please login manually.")
        self.driver.get("https://mail.google.com/")
        start = time.time()
        while time.time() - start < timeout:
            if self._is_google_logged_in():
                logger.info("Google account login detected.")
                break
            time.sleep(2)
        else:
            raise LoginFailedException("Timeout: please login to Gmail in the browser window first.")

        logger.info("Google login detected; returning to LeetCode login page.")
        self.driver.get("https://leetcode.com/accounts/login/")
        if self._click_google_button():
            logger.info("Clicked Google sign-in button on LeetCode.")
        else:
            logger.info("Please click the Google sign-in button on LeetCode login page manually.")

        start = time.time()
        while time.time() - start < timeout:
            if self._is_logged_in():
                logger.info("Login detected, continuing.")
                return
            try:
                if "accounts/login" not in self.driver.current_url.lower():
                    logger.info("URL changed from login page, assuming logged in.")
                    return
            except Exception:
                pass
            time.sleep(2)

        raise LoginFailedException("Timeout: please complete the login process on the opened browser window.")

    def login(self) -> None:
        self.ensure_login()
