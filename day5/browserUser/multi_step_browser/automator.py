from playwright.sync_api import sync_playwright, Playwright, Browser, BrowserContext
from .agent import AgentSession

class BrowserAutomator:
    def __init__(self, browser_type: str = "chromium", headless: bool = False, slow_mo: int = 50):
        self.browser_type = browser_type
        self.headless = headless
        self.slow_mo = slow_mo
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        browser_launcher = getattr(self.playwright, self.browser_type)
        self.browser = browser_launcher.launch(headless=self.headless, slow_mo=self.slow_mo)
        return self

    def new_agent(self) -> AgentSession:
        if not self.browser:
            raise Exception("Browser not started. Call start() or use as a context manager.")
        context: BrowserContext = self.browser.new_context()
        return AgentSession(context)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    # Kept for non-context manager usage, though context manager is preferred.
    def start(self):
        """Manually starts the playwright instance and browser."""
        if self.playwright is None: # Ensure not to restart if already started
            self.playwright = sync_playwright().start()
            browser_launcher = getattr(self.playwright, self.browser_type)
            self.browser = browser_launcher.launch(headless=self.headless, slow_mo=self.slow_mo)
        return self

    def close(self):
        """Manually closes the browser and playwright instance."""
        if self.browser:
            self.browser.close()
            self.browser = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None 