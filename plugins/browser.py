from agents import Tool
from agents.mcp import MCPServer

from browser import BrowserSession
from config import Config


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
