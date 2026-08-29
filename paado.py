from agents import Agent, function_tool

from browser import BrowserThread
from config import Config


class Paado:
    def __init__(self, config: Config, agent: Agent):
        self.browser = BrowserThread(config)
        self.agent = agent.clone(
            name="Paado",
            instructions=(
                "You are Paado. The user message is the task. "
                "Use the browser tools immediately. Do not ask what the task is."
            ),
            tools=self._tools(),
        )

    def _tools(self):
        browser = self.browser

        @function_tool
        def do_navigate(url: str) -> str:
            """Navigate the browser to the given URL."""
            browser.do_navigate(url)
            return "ok"

        @function_tool
        def do_read_html() -> str:
            """Return the current page HTML."""
            return browser.do_read_html()

        @function_tool
        def do_click(selector: str) -> str:
            """Click the element matching the CSS selector."""
            browser.do_click(selector)
            return "ok"

        @function_tool
        def do_type(selector: str, text: str) -> str:
            """Type text into the element matching the CSS selector."""
            browser.do_type(selector, text)
            return "ok"

        return [do_navigate, do_read_html, do_click, do_type]

    def close(self):
        self.browser.close()
