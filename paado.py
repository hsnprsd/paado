from agents import Agent

from plugins import Plugin


class Paado:
    def __init__(self, agent: Agent, plugins: list[Plugin]):
        self.plugins = plugins
        self.agent = agent.clone(
            name="Paado",
            instructions=(
                "You are Paado. Complete the user's task."
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
