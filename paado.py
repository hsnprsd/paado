from agents import Agent

from plugins import Plugin


class Paado:
    def __init__(self, agent: Agent, plugins: list[Plugin]):
        self.plugins = plugins
        self.agent = agent.clone(
            name="Paado",
            instructions=(
                "You are Paado. Complete the user's task using the tools.\n"
                "\n"
                "Browser:\n"
                "- do_navigate(url): open a page. url must be absolute (include https://).\n"
                "- do_read_html(): get the current page HTML so you can find CSS selectors.\n"
                "- do_click(selector): click the first element matching the CSS selector.\n"
                "- do_type(selector, text): replace the field's value. Does not submit; "
                "click the submit control after typing if you need to.\n"
                "Read the page after navigate and after any action that changes it.\n"
                "\n"
                "Terminal:\n"
                "- do_exec(script): run bash in a new process. Check `exit code` in the result.\n"
            ),
            tools=[tool for plugin in plugins for tool in plugin.tools()],
        )

    async def start(self):
        for plugin in self.plugins:
            await plugin.start()

    async def close(self):
        for plugin in reversed(self.plugins):
            await plugin.close()
