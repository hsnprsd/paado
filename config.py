from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class StdioMCPServerConfig(BaseModel):
    transport: Literal["stdio"] = "stdio"
    command: str
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)
    cwd: Path | None = None
    timeout: float = 30


class HttpMCPServerConfig(BaseModel):
    transport: Literal["streamable_http"]
    url: str
    headers: dict[str, str] = Field(default_factory=dict)
    timeout: float = 30
    sse_read_timeout: float = 300
    terminate_on_close: bool = True


class SseMCPServerConfig(BaseModel):
    transport: Literal["sse"]
    url: str
    headers: dict[str, str] = Field(default_factory=dict)
    timeout: float = 30
    sse_read_timeout: float = 300


MCPServerConfig = StdioMCPServerConfig | HttpMCPServerConfig | SseMCPServerConfig


def default_mcp_servers() -> dict[str, MCPServerConfig]:
    return {
        "playwright": StdioMCPServerConfig(
            command="npx",
            args=["@playwright/mcp@latest", "--headless"],
        )
    }


class Config(BaseSettings):
    ollama_host: str = "http://127.0.0.1:11434"
    model: str = "gemma4:12b"
    context_length: int = 64 * 1024
    thinking_effort: Literal["none", "low", "medium", "high"] = "low"
    mcp_servers: dict[str, MCPServerConfig] = Field(
        default_factory=default_mcp_servers
    )
