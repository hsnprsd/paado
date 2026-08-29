from agents import Tool, function_tool

from browser import BrowserSession
from config import Config


class BrowserPlugin:
    def __init__(self, config: Config):
        self.browser = BrowserSession(config)

    def tools(self) -> list[Tool]:
        browser = self.browser

        @function_tool
        async def do_navigate(url: str) -> str:
            """Open a web page. Wait until the page has finished loading.

            Args:
                url: Absolute URL including the scheme, e.g. https://en.wikipedia.org/.
                    Relative paths are not accepted.
            """
            await browser.do_navigate(url)
            return "ok"

        @function_tool
        async def do_read_html() -> str:
            """Return the full HTML of the current page.

            Use this after navigating or after click/type that may have changed the
            page. Read the HTML to find CSS selectors for links, buttons, and inputs.
            """
            return await browser.do_read_html()

        @function_tool
        async def do_click(selector: str) -> str:
            """Click one element on the current page.

            Args:
                selector: CSS selector for the element, e.g. `#searchButton`,
                    `button[type='submit']`, or `a[href='/wiki/Hello,_world']`.
                    If several elements match, the first one is clicked.
            """
            await browser.do_click(selector)
            return "ok"

        @function_tool
        async def do_type(selector: str, text: str) -> str:
            """Fill an input, textarea, or contenteditable field.

            Replaces any existing value. Does not press Enter or submit the form;
            call do_click on the submit control afterward if needed.

            Args:
                selector: CSS selector for the field, e.g. `input[name='search']`
                    or `#searchInput`.
                text: The full text to put in the field.
            """
            await browser.do_type(selector, text)
            return "ok"

        return [do_navigate, do_read_html, do_click, do_type]

    async def start(self):
        await self.browser.start()

    async def close(self):
        await self.browser.close()
