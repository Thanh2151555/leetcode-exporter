import os
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions


class ChromeSessionManager:
    def __init__(
        self,
        headless: bool = True,
        user_data_dir: Optional[str] = None,
        profile_dir: str = "Default",
        browser: str = "chrome",
    ) -> None:
        self.headless = headless
        self.user_data_dir = user_data_dir
        self.profile_dir = profile_dir
        self.browser = browser.lower()
        self.driver = None

    def _resolve_user_data_dir(self) -> Optional[str]:
        if self.user_data_dir:
            return self.user_data_dir

        local_app_data = os.getenv("LOCALAPPDATA")
        if not local_app_data:
            return None

        candidates = [
            os.path.join(local_app_data, "Google", "Chrome", "User Data"),
            os.path.join(local_app_data, "Microsoft", "Edge", "User Data"),
        ]

        for path in candidates:
            if os.path.exists(path):
                return path

        return None

    def _find_browser_binary(self) -> Optional[str]:
        search_paths = []
        if self.browser == "chrome":
            search_paths.extend([
                os.path.join(os.getenv("ProgramFiles", r"C:\Program Files"), "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(os.getenv("ProgramFiles(x86)", r"C:\Program Files (x86)"), "Google", "Chrome", "Application", "chrome.exe"),
            ])
        elif self.browser == "edge":
            search_paths.extend([
                os.path.join(os.getenv("ProgramFiles", r"C:\Program Files"), "Microsoft", "Edge", "Application", "msedge.exe"),
                os.path.join(os.getenv("ProgramFiles(x86)", r"C:\Program Files (x86)"), "Microsoft", "Edge", "Application", "msedge.exe"),
            ])
        else:
            search_paths.extend([
                os.path.join(os.getenv("ProgramFiles", r"C:\Program Files"), "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(os.getenv("ProgramFiles(x86)", r"C:\Program Files (x86)"), "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(os.getenv("ProgramFiles", r"C:\Program Files"), "Microsoft", "Edge", "Application", "msedge.exe"),
                os.path.join(os.getenv("ProgramFiles(x86)", r"C:\Program Files (x86)"), "Microsoft", "Edge", "Application", "msedge.exe"),
            ])

        for path in search_paths:
            if os.path.exists(path):
                return path

        return None

    def start(self):
        if self.browser == "edge":
            from selenium.webdriver.edge.service import Service as EdgeService
            from webdriver_manager.microsoft import EdgeChromiumDriverManager
            
            options = EdgeOptions()
            if self.headless:
                options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--remote-debugging-port=0")
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-extensions")
            options.add_argument("--window-size=1400,1000")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)

            if self.user_data_dir:
                options.add_argument(f"--user-data-dir={self.user_data_dir}")
                options.add_argument(f"--profile-directory={self.profile_dir}")
            
            self.driver = webdriver.Edge(
                service=EdgeService(EdgeChromiumDriverManager().install()),
                options=options
            )
        else:
            import undetected_chromedriver as uc
            
            options = uc.ChromeOptions()
            if self.headless:
                options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--window-size=1400,1000")
            
            browser_binary = self._find_browser_binary()
            if browser_binary:
                options.binary_location = browser_binary

            if self.user_data_dir:
                options.add_argument(f"--user-data-dir={self.user_data_dir}")
                options.add_argument(f"--profile-directory={self.profile_dir}")

            # Try creating the Chrome driver. If it fails (common when a user-data
            # profile is locked or incompatible), retry without the user-data args.
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                driver_path = ChromeDriverManager().install()
                self.driver = uc.Chrome(options=options, driver_executable_path=driver_path)
            except Exception as exc:
                # Remove profile options and retry
                try:
                    logger = __import__('logging').getLogger(__name__)
                    logger.warning("Failed to start Chrome with user profile, retrying without profile: %s", exc)
                except Exception:
                    pass

                # rebuild options without user-data args
                options = uc.ChromeOptions()
                if self.headless:
                    options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")
                options.add_argument("--no-first-run")
                options.add_argument("--no-default-browser-check")
                options.add_argument("--window-size=1400,1000")
                if browser_binary:
                    options.binary_location = browser_binary

                from webdriver_manager.chrome import ChromeDriverManager
                driver_path = ChromeDriverManager().install()
                self.driver = uc.Chrome(options=options, driver_executable_path=driver_path)

        self.driver.implicitly_wait(10)
        
        try:
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            })
        except Exception:
            pass

        return self.driver

    def quit(self) -> None:
        if self.driver:
            self.driver.quit()
            self.driver = None

    def get_driver(self):
        if not self.driver:
            raise RuntimeError("ChromeSessionManager not started. Call start() first.")
        return self.driver
