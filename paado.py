from agents import Agent, function_tool

from browser import BrowserSession
from config import Config


class Paado:
    def __init__(self, config: Config, agent: Agent):
        self.browser = BrowserSession(config)
        self.agent = agent.clone(
            name="Paado",
            instructions=(
                "You are Paado. Complete the user's task using the browser tools."
            ),
            tools=self._tools(),
        )

    def _tools(self):
        browser = self.browser

        @function_tool
        async def do_navigate(url: str) -> str:
            """Navigate the browser to the given URL."""
            await browser.do_navigate(url)
            return "ok"

        @function_tool
        async def do_read_html() -> str:
            """Return the current page HTML."""
            return await browser.do_read_html()

        @function_tool
        async def do_click(selector: str) -> str:
            """Click the element matching the CSS selector."""
            await browser.do_click(selector)
            return "ok"

        @function_tool
        async def do_type(selector: str, text: str) -> str:
            """Type text into the element matching the CSS selector."""
            await browser.do_type(selector, text)
            return "ok"

        return [do_navigate, do_read_html, do_click, do_type]

    async def start(self):
        await self.browser.start()

    async def close(self):
        await self.browser.close()
