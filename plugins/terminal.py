from agents import Tool, function_tool
from agents.mcp import MCPServer

from config import Config
from terminal import TerminalSession


class TerminalPlugin:
    def __init__(self, config: Config):
        self.terminal = TerminalSession(config)

    def tools(self) -> list[Tool]:
        terminal = self.terminal

        @function_tool
        async def do_exec(script: str) -> str:
            """Run a bash script and return its output.

            Starts a fresh bash process each call (working directory and environment
            do not persist). The process is killed after 60 seconds. The result is
            combined stdout/stderr, then a final line `exit code: N`.

            Args:
                script: Bash source to run, e.g. `ls -la` or a multi-line script.
                    Do not wrap it in `bash -c`; it is already executed with bash.
            """
            return await terminal.do_exec(script)

        return [do_exec]

    def mcp_servers(self) -> list[MCPServer]:
        return []

    async def start(self):
        await self.terminal.start()

    async def close(self):
        await self.terminal.close()
