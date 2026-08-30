# Paado

## Built-in filesystem access

Paado always enables the official Filesystem MCP server. It runs locally through
`npx` and can read, search, create, edit, move, and delete files anywhere the
user running Paado has permission to access. Node.js and npm must be installed.

The built-in server currently tracks the latest npm release and is launched as:

```bash
npx -y @modelcontextprotocol/server-filesystem@latest /
```

This deliberately grants the server `/` as its allowed directory and does not
require confirmation for file changes. Use it only in an environment where that
level of access is acceptable.

## Custom MCP servers

Custom MCP servers can be supplied through the `mcp_servers` object in
`config.json`. Object keys become server names. Paado supports stdio, streamable
HTTP, and legacy SSE transports. When `mcp_servers` is omitted, Paado also
enables the headless Playwright MCP server:

```json
{
  "playwright": {
    "command": "npx",
    "args": ["@playwright/mcp@latest", "--headless"]
  }
}
```

Setting `mcp_servers` replaces the Playwright default, so include the Playwright
entry if browser tools should remain available alongside custom servers. The
built-in Filesystem server is added even when custom servers are present. A
custom entry named `filesystem` overrides its command, arguments, and scope.

```json
{
  "model": "your-ollama-model",
  "mcp_servers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--headless"]
    },
    "remote": {
      "transport": "streamable_http",
      "url": "https://example.com/mcp",
      "headers": {"Authorization": "Bearer token"}
    }
  }
}
```

The same structure can be passed directly in Python:

```python
from config import Config

config = Config(
    model="your-ollama-model",
    mcp_servers={
        "local": {
            "transport": "stdio",
            "command": "my-mcp-server",
            "args": ["--flag"],
        }
    },
)
```
