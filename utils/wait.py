from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def wait_for_condition(driver: WebDriver, locator, timeout: int = 20):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))


def retry(action, retries: int = 3, delay: float = 1.0):
    import time

    last_exception = None
    for attempt in range(1, retries + 1):
        try:
            return action()
        except WebDriverException as exc:
            last_exception = exc
            if attempt == retries:
                raise
            time.sleep(delay)
    raise last_exception
