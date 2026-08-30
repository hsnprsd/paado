from agents import Tool
from agents.mcp import MCPServer, MCPServerStdio, MCPServerStdioParams

from config import Config


class BrowserSession:
    def __init__(self, config: Config):
        self._config = config
        args = ["@playwright/mcp@latest"]
        args.append("--headless")
        self.server = MCPServerStdio(
            MCPServerStdioParams(
                command="npx",
                args=args,
            ),
            client_session_timeout_seconds=30,
        )

    async def start(self):
        await self.server.connect()

    async def close(self):
        await self.server.cleanup()


class BrowserPlugin:
    def __init__(self, config: Config):
        self.browser = BrowserSession(config)

    def tools(self) -> list[Tool]:
        return []

    def mcp_servers(self) -> list[MCPServer]:
        return [self.browser.server]

    async def start(self):
        await self.browser.start()

    async def close(self):
        await self.browser.close()
