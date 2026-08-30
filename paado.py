from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from agents import Agent
from jinja2 import Template

from plugins import Plugin

SYSTEM_PROMPT = Path(__file__).with_name("prompts").joinpath("paado.md").read_text()


def render_system_prompt() -> str:
    return Template(SYSTEM_PROMPT).render(
        current_date=datetime.now(tz=ZoneInfo("Asia/Tehran")).date().isoformat()
    )


class Paado:
    def __init__(self, agent: Agent, plugins: list[Plugin]):
        self.plugins = plugins
        self.agent = agent.clone(
            name="Paado",
            instructions=render_system_prompt(),
            tools=[tool for plugin in plugins for tool in plugin.tools()],
            mcp_servers=[server for plugin in plugins for server in plugin.mcp_servers()],
        )

    async def start(self):
        for plugin in self.plugins:
            await plugin.start()

    async def close(self):
        for plugin in reversed(self.plugins):
            await plugin.close()
