import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--user-data-dir=.selenium_user_data")
options.add_argument("--profile-directory=Default")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

driver.get("https://leetcode.com/problemset/?status=AC")
time.sleep(10)

with open("leetcode_dump.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)

driver.quit()
