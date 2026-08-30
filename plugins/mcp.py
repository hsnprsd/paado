from agents import Tool
from agents.mcp import (
    MCPServer,
    MCPServerSse,
    MCPServerSseParams,
    MCPServerStdio,
    MCPServerStdioParams,
    MCPServerStreamableHttp,
    MCPServerStreamableHttpParams,
)

from config import (
    HttpMCPServerConfig,
    MCPServerConfig,
    SseMCPServerConfig,
    StdioMCPServerConfig,
)


def build_mcp_server(name: str, config: MCPServerConfig) -> MCPServer:
    if isinstance(config, StdioMCPServerConfig):
        params = MCPServerStdioParams(
            command=config.command,
            args=config.args,
            env=config.env,
            **({"cwd": config.cwd} if config.cwd is not None else {}),
        )
        return MCPServerStdio(
            params,
            name=name,
            client_session_timeout_seconds=config.timeout,
        )

    common = {
        "url": config.url,
        "headers": config.headers,
        "timeout": config.timeout,
        "sse_read_timeout": config.sse_read_timeout,
    }
    if isinstance(config, HttpMCPServerConfig):
        return MCPServerStreamableHttp(
            MCPServerStreamableHttpParams(
                **common,
                terminate_on_close=config.terminate_on_close,
            ),
            name=name,
            client_session_timeout_seconds=config.timeout,
        )
    if isinstance(config, SseMCPServerConfig):
        return MCPServerSse(
            MCPServerSseParams(**common),
            name=name,
            client_session_timeout_seconds=config.timeout,
        )
    raise TypeError(f"Unsupported MCP server configuration: {type(config).__name__}")


class MCPPlugin:
    def __init__(self, configs: dict[str, MCPServerConfig]):
        self.servers = [build_mcp_server(name, config) for name, config in configs.items()]
        self._connected: list[MCPServer] = []

    def tools(self) -> list[Tool]:
        return []

    def mcp_servers(self) -> list[MCPServer]:
        return self.servers

    async def start(self) -> None:
        try:
            for server in self.servers:
                await server.connect()
                self._connected.append(server)
        except BaseException:
            await self.close()
            raise

    async def close(self) -> None:
        while self._connected:
            await self._connected.pop().cleanup()
