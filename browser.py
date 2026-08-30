from os import environ
import os

from agents.mcp import MCPServerStdio, MCPServerStdioParams

from config import Config


class BrowserSession:
    def __init__(self, config: Config):
        self._config = config
        args = ["@playwright/mcp@latest"]
        if config.chrome_headless:
            args.append("--headless")
        args.append("--extension")
        args.append(f"--executable-path={config.chrome_path}")

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
