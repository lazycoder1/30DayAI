from playwright.sync_api import BrowserContext, Page

class AgentSession:
    def __init__(self, browser_context: BrowserContext):
        self.context: BrowserContext = browser_context
        self.page: Page = self.context.new_page()

    def navigate(self, url: str):
        self.page.goto(url)

    def click(self, selector: str):
        self.page.locator(selector).click()

    def fill(self, selector: str, text: str):
        self.page.locator(selector).fill(text)

    def get_text(self, selector: str) -> str:
        return self.page.locator(selector).text_content() or ""

    def close(self):
        # The page will be closed when the context is closed,
        # and the context will be closed when the browser is closed by the Automator.
        # However, providing an explicit close for the page if needed.
        if self.page and not self.page.is_closed():
            self.page.close() 