from playwright.async_api import Browser, Playwright, async_playwright

from config import Config


class BrowserSession:
    def __init__(self, config: Config):
        self._config = config

    async def start(self):
        self._playwright: Playwright = await async_playwright().start()
        self.browser: Browser = await self._playwright.chromium.launch(
            executable_path=self._config.chrome_path, headless=self._config.chrome_headless
        )
        self.page = await self.browser.new_page()

    async def do_navigate(self, url: str):
        await self.page.goto(url, wait_until="networkidle")

    async def do_read_html(self) -> str:
        return await self.page.content()

    async def do_click(self, selector: str):
        await self.page.click(selector)

    async def do_type(self, selector: str, text: str):
        await self.page.fill(selector, text)

    async def do_keypress(self, key: str):
        await self.page.keyboard.press(key)

    async def close(self):
        await self.browser.close()
        await self._playwright.stop()
