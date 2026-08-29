from agents import Tool, function_tool

from config import Config
from terminal import TerminalSession


class TerminalPlugin:
    def __init__(self, config: Config):
        self.terminal = TerminalSession(config)

    def tools(self) -> list[Tool]:
        terminal = self.terminal

        @function_tool
        async def do_exec(script: str) -> str:
            """Execute a bash script and return its output and exit code."""
            return await terminal.do_exec(script)

        return [do_exec]

    async def start(self):
        await self.terminal.start()

    async def close(self):
        await self.terminal.close()
