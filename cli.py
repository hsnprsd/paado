import argparse
import asyncio
import json
import sys

from agents.stream_events import RawResponsesStreamEvent, RunItemStreamEvent
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from config import Config
from loop import Loop
from paado import Paado
from plugins.mcp import MCPPlugin
from providers import OllamaProvider

console = Console()

_THINKING_EVENTS = {
    "response.reasoning_text.delta",
    "response.reasoning_summary_text.delta",
}
_OUTPUT_MAX = 200


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="paado", description="Paado agent")
    parser.add_argument("-m", "--model", help="Model name")
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(run(args))
    except KeyboardInterrupt:
        console.print()
        sys.exit(130)


async def run(args: argparse.Namespace) -> None:
    config = Config()
    provider = OllamaProvider(config)
    model = args.model or config.model
    paado = Paado(
        provider.model(model),
        plugins=[
            MCPPlugin(config.mcp_servers),
        ],
    )
    console.print(Panel.fit(f"[bold]Paado[/bold]\n[dim]{model}[/dim]"))
    await paado.start()
    try:
        await _repl(paado.agent)
    finally:
        await paado.close()


async def _run_task(
    loop: Loop,
    task: str,
) -> None:
    result = loop.stream(task)
    display = _RunDisplay()
    async for event in result.stream_events():
        display.handle(event)
    display.finish(result.final_output)


async def _repl(agent) -> None:
    while True:
        async with Loop(agent) as loop:
            while True:
                task = Prompt.ask("[bold cyan]paado[/]")
                if task == "/quit":
                    return
                if task == "/clear":
                    console.print("[dim]Started a new session.[/]")
                    break
                await _run_task(loop, task)


class _RunDisplay:
    def __init__(self):
        self._need_nl = False
        self._thinking = False

    def handle(self, event) -> None:
        if isinstance(event, RawResponsesStreamEvent):
            etype = getattr(event.data, "type", None)
            delta = getattr(event.data, "delta", None)
            if etype in _THINKING_EVENTS and delta:
                self._thinking_delta(delta)
            return
        if isinstance(event, RunItemStreamEvent):
            if event.name == "reasoning_item_created":
                self._end_thinking()
            elif event.name == "tool_called":
                self._end_thinking()
                self._tool_called(event.item)
            elif event.name == "tool_output":
                self._tool_output(event.item.output)
            elif event.name == "message_output_created":
                self._end_thinking()

    def finish(self, final_output) -> None:
        self._end_thinking()
        if final_output:
            console.print(Markdown(str(final_output)))

    def _thinking_delta(self, delta: str) -> None:
        if not self._thinking:
            self._break()
            console.print("[dim italic]thinking[/]")
            self._thinking = True
        console.print(delta, end="", style="dim italic", markup=False, highlight=False)
        self._need_nl = True

    def _end_thinking(self) -> None:
        if not self._thinking:
            return
        self._thinking = False
        self._break()

    def _tool_called(self, item) -> None:
        self._break()
        name = getattr(item, "tool_name", None) or "tool"
        args = _format_tool_args(item)
        console.print(f"[cyan]→ {name}[/]", end=" " if args else "\n")
        if args:
            console.print(args, style="dim", markup=False, highlight=False)

    def _tool_output(self, output) -> None:
        self._break()
        text = " ".join(str(output).split())
        if len(text) > _OUTPUT_MAX:
            text = text[:_OUTPUT_MAX] + "…"
        console.print("← ", style="dim", end="")
        console.print(text, style="dim", markup=False, highlight=False)

    def _break(self) -> None:
        if self._need_nl:
            console.print()
            self._need_nl = False


def _format_tool_args(item) -> str:
    raw = getattr(item, "raw_item", None)
    if isinstance(raw, dict):
        payload = raw.get("arguments") or ""
    else:
        payload = getattr(raw, "arguments", None) or ""
    if not payload:
        return ""
    try:
        parsed = json.loads(payload)
    except (TypeError, json.JSONDecodeError):
        return str(payload)
    if isinstance(parsed, dict):
        return " ".join(f"{key}={value}" for key, value in parsed.items())
    return str(payload)


if __name__ == "__main__":
    main()
