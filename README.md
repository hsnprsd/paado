# Paado

## Custom MCP servers

Custom MCP servers can be supplied through the `MCP_SERVERS` setting as a JSON
object. Object keys become server names. Paado supports stdio, streamable HTTP,
and legacy SSE transports. By default, this setting contains the headless
Playwright MCP server:

```json
{
  "playwright": {
    "command": "npx",
    "args": ["@playwright/mcp@latest", "--headless"]
  }
}
```

Setting `MCP_SERVERS` replaces that default, so include the Playwright entry if
browser tools should remain available alongside custom servers.

```bash
export MCP_SERVERS='{
  "filesystem": {
    "transport": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
  },
  "remote": {
    "transport": "streamable_http",
    "url": "https://example.com/mcp",
    "headers": {"Authorization": "Bearer token"}
  }
}'

paado
```

The same structure can be passed directly in Python:

```python
from config import Config

config = Config(mcp_servers={
    "local": {
        "transport": "stdio",
        "command": "my-mcp-server",
        "args": ["--flag"],
    }
})
```
