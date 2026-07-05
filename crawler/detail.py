import logging
import re
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from models.submission import SubmissionCode
from utils.exceptions import CrawlerException


logger = logging.getLogger(__name__)


class SubmissionDetailCrawler:
    def __init__(self, driver: Chrome) -> None:
        self.driver = driver

    def extract_code(self, submission_url: str) -> SubmissionCode:
        """Extract source code from submission detail page via GraphQL."""
        logger.info("Extracting code from submission: %s", submission_url)
        
        match = re.search(r"/submissions/(?:detail/)?(\d+)", submission_url)
        if match:
            submission_id = match.group(1)
            script = """
            var callback = arguments[arguments.length - 1];
            var submissionId = parseInt(arguments[0]);
            var getCookie = function(name) {
                var value = "; " + document.cookie;
                var parts = value.split("; " + name + "=");
                if (parts.length == 2) return parts.pop().split(";").shift();
            };
            fetch('https://leetcode.com/graphql', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-csrftoken': getCookie('csrftoken') || ''
                },
                body: JSON.stringify({
                    query: `query submissionDetails($submissionId: Int!) {
                      submissionDetails(submissionId: $submissionId) {
                        code
                        lang {
                          name
                        }
                      }
                    }`,
                    variables: { submissionId: submissionId }
                })
            })
            .then(r => r.json())
            .then(data => callback(data))
            .catch(err => callback({error: err.toString()}));
            """
            
            try:
                self.driver.set_script_timeout(15)
                result = self.driver.execute_async_script(script, submission_id)
                if result and "data" in result and result["data"] and "submissionDetails" in result["data"]:
                    details = result["data"]["submissionDetails"]
                    code = details.get("code")
                    lang_name = details.get("lang", {}).get("name", "unknown")
                    
                    if code:
                        logger.info("Extracted %s code from submission (%d chars) via API", lang_name.upper(), len(code))
                        return SubmissionCode(language=lang_name.lower(), code=code, url=submission_url)
            except Exception as e:
                logger.warning("GraphQL submission extraction failed: %s", e)
        
        # DOM Fallback
        self.driver.get(submission_url)
        try:
            # wait for monaco editor lines
            lines = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".view-lines .view-line"))
            )
            # click view more if it exists
            try:
                view_more = self.driver.find_element(By.XPATH, "//*[contains(text(), 'View more') or contains(text(), 'Show more')]")
                view_more.click()
                import time
                time.sleep(1)
                lines = self.driver.find_elements(By.CSS_SELECTOR, ".view-lines .view-line")
            except NoSuchElementException:
                pass
            
            code = "\\n".join([line.text for line in lines])
            if code:
                return SubmissionCode(language="unknown", code=code, url=submission_url)
        except Exception as e:
            logger.error("Failed to extract code from submission via DOM: %s", str(e))
            raise CrawlerException("Failed to extract code from submission") from e
            
        raise CrawlerException("Failed to extract code from submission")
