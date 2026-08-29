from playwright.sync_api import Browser, Playwright, sync_playwright

from config import Config


class BrowserSession:
    def __init__(self, config: Config):
        self._playwright: Playwright = sync_playwright().start()
        self.browser: Browser = self._playwright.chromium.launch(
            executable_path=config.chrome_path, headless=config.chrome_headless
        )
        self.page = self.browser.new_page()

    def do_navigate(self, url: str):
        self.page.goto(url, wait_until="networkidle")

    def do_read_html(self) -> str:
        return self.page.content()

    def do_click(self, selector: str):
        self.page.click(selector)

    def do_type(self, selector: str, text: str):
        self.page.fill(selector, text)

    def close(self):
        self.browser.close()
        self._playwright.stop()
