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
                "Use the browser MCP server (e.g. browser_navigate, browser_click, browser_type, "
                "browser_snapshot, browser_press_key, browser_select_option, etc.) to interact with web pages.\n"
                "Inspect the page structure using snapshots and perform actions using element references.\n"
                "\n"
                "Terminal:\n"
                "- do_exec(script): run bash in a new process. Check `exit code` in the result.\n"
            ),
            tools=[tool for plugin in plugins for tool in plugin.tools()],
            mcp_servers=[server for plugin in plugins for server in plugin.mcp_servers()],
        )

    async def start(self):
        for plugin in self.plugins:
            await plugin.start()

    async def close(self):
        for plugin in reversed(self.plugins):
            await plugin.close()
