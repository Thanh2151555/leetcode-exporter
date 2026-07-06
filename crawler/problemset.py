import logging
import re
from typing import List

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from models.submission import LeetCodeProblem
from utils.exceptions import CrawlerException


logger = logging.getLogger("leetcode_exporter")


class ProblemSetCrawler:
    def __init__(self, driver: Chrome) -> None:
        self.driver = driver

    def collect_solved_problems(self) -> List[LeetCodeProblem]:
        """Collect all solved problems using LeetCode GraphQL API."""
        logger.info("Collecting solved problems via LeetCode GraphQL API")
        self.driver.get("https://leetcode.com/")
        
        script = """
        var callback = arguments[arguments.length - 1];
        var getCookie = function(name) {
            var value = "; " + document.cookie;
            var parts = value.split("; " + name + "=");
            if (parts.length == 2) return parts.pop().split(";").shift();
        };
        var csrfToken = getCookie("csrftoken");
        
        var allQuestions = [];
        var skip = 0;
        var limit = 100;
        
        function fetchPage() {
            fetch('https://leetcode.com/graphql', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-csrftoken': csrfToken || ''
                },
                body: JSON.stringify({
                    query: `query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
                      problemsetQuestionList: questionList(
                        categorySlug: $categorySlug
                        limit: $limit
                        skip: $skip
                        filters: $filters
                      ) {
                        questions: data {
                          frontendQuestionId: questionFrontendId
                          title
                          titleSlug
                        }
                      }
                    }`,
                    variables: {
                        categorySlug: "",
                        skip: skip,
                        limit: limit,
                        filters: { status: "AC" }
                    }
                })
            })
            .then(r => r.json())
            .then(data => {
                var questions = [];
                if (data && data.data && data.data.problemsetQuestionList && data.data.problemsetQuestionList.questions) {
                    questions = data.data.problemsetQuestionList.questions;
                }
                allQuestions = allQuestions.concat(questions);
                
                if (questions.length === limit) {
                    skip += limit;
                    fetchPage();
                } else {
                    callback({ data: { problemsetQuestionList: { questions: allQuestions } } });
                }
            })
            .catch(err => callback({error: err.toString()}));
        }
        
        fetchPage();
        """

        solved: List[LeetCodeProblem] = []
        try:
            self.driver.set_script_timeout(120)
            result = self.driver.execute_async_script(script)
            
            if result and "data" in result and result["data"] and "problemsetQuestionList" in result["data"]:
                questions = result["data"]["problemsetQuestionList"]["questions"]
                for q in questions:
                    solved.append(LeetCodeProblem(
                        problem_id=q.get("frontendQuestionId", "0"),
                        title=q.get("title", ""),
                        slug=q.get("titleSlug", "")
                    ))
                    logger.debug("Found solved problem via GraphQL: %s - %s", q.get("frontendQuestionId"), q.get("title"))
                
                logger.info("Collected %d solved problems via API", len(solved))
            else:
                logger.error("GraphQL response did not contain expected data: %s", result)
                raise CrawlerException("Invalid GraphQL response")
        except Exception as exc:
            logger.error("Failed to collect solved problems via GraphQL: %s", str(exc))
            raise CrawlerException("Failed to collect solved problems") from exc

        return solved
