import logging
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from models.submission import LeetCodeProblem
from utils.exceptions import CrawlerException


logger = logging.getLogger(__name__)


class SubmissionCrawler:
    def __init__(self, driver: Chrome) -> None:
        self.driver = driver

    def open_problem_submissions(self, problem: LeetCodeProblem) -> str:
        """Get the URL of the latest accepted submission using GraphQL."""
        logger.info("Finding accepted submission for problem %s - %s", problem.problem_id, problem.title)
        
        script = """
        var callback = arguments[arguments.length - 1];
        var slug = arguments[0];
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
                query: `query submissionList($offset: Int!, $limit: Int!, $questionSlug: String!) {
                  submissionList(offset: $offset, limit: $limit, questionSlug: $questionSlug) {
                    submissions {
                      id
                      lang
                      statusDisplay
                      url
                    }
                  }
                }`,
                variables: { offset: 0, limit: 20, questionSlug: slug }
            })
        })
        .then(r => r.json())
        .then(data => callback(data))
        .catch(err => callback({error: err.toString()}));
        """
        
        try:
            self.driver.set_script_timeout(15)
            result = self.driver.execute_async_script(script, problem.slug)
            
            if result and "data" in result and result["data"] and "submissionList" in result["data"]:
                submissions = result["data"]["submissionList"]["submissions"]
                for sub in submissions:
                    if sub.get("statusDisplay") == "Accepted":
                        sub_id = sub.get("id")
                        logger.info("Found accepted submission ID: %s", sub_id)
                        return f"https://leetcode.com/problems/{problem.slug}/submissions/{sub_id}/"
        except Exception as e:
            logger.warning("Failed to fetch submissions via GraphQL for %s: %s", problem.slug, str(e))
            
        # Fallback
        return f"https://leetcode.com/problems/{problem.slug}/"
