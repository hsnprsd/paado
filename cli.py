import argparse
import asyncio
import sys

from agents.stream_events import RawResponsesStreamEvent, RunItemStreamEvent
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from config import Config
from loop import Loop
from paado import Paado
from plugins.browser import BrowserPlugin
from plugins.terminal import TerminalPlugin
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
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("--headless", action="store_true", help="Run Chrome headless")
    parser.add_argument("task", nargs="*", help="Task to run (interactive if omitted)")
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(run(args))
    except KeyboardInterrupt:
        console.print()
        sys.exit(130)


async def run(args: argparse.Namespace) -> None:
    config = Config(**({"chrome_headless": True} if args.headless else {}))
    provider = OllamaProvider(config)
    models = provider.list_available_models()
    if not models:
        console.print("[red]No Ollama models available.[/red]")
        raise SystemExit(1)

    if args.list_models:
        for name in models:
            console.print(name)
        return

    model = args.model or models[0]
    paado = Paado(
        provider.model(model),
        plugins=[BrowserPlugin(config), TerminalPlugin(config)],
    )
    console.print(Panel.fit(f"[bold]Paado[/bold]\n[dim]{model}[/dim]"))
    await paado.start()
    try:
        task = " ".join(args.task).strip()
        if task:
            await _run_task(paado, task, config.context_length)
            return
        await _repl(paado, config.context_length)
    finally:
        await paado.close()


async def _run_task(paado: Paado, task: str, context_length: int) -> None:
    result = Loop(paado.agent).stream(task)
    display = _RunDisplay()
    async for event in result.stream_events():
        display.handle(event)
    display.finish(result.final_output, result.context_wrapper.usage, context_length)


async def _repl(paado: Paado, context_length: int) -> None:
    while True:
        try:
            task = Prompt.ask("[bold cyan]paado[/]").strip()
        except EOFError:
            console.print()
            return
        if not task:
            continue
        if task.lower() in {"exit", "quit", "q"}:
            return
        await _run_task(paado, task, context_length)


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
            if event.name == "tool_called":
                self._tool_called(event.item)
            elif event.name == "tool_output":
                self._tool_output(event.item.output)

    def finish(self, final_output, usage, context_length: int) -> None:
        self._break()
        if final_output:
            console.print(Markdown(str(final_output)))
        console.print(f"[dim]{_format_tokens(usage, context_length)}[/]")

    def _thinking_delta(self, delta: str) -> None:
        if not self._thinking:
            self._break()
            console.print("[dim italic]thinking[/]")
            self._thinking = True
        console.print(delta, end="", style="dim italic", markup=False, highlight=False)
        self._need_nl = True

    def _tool_called(self, item) -> None:
        self._thinking = False
        self._break()
        name = getattr(item, "tool_name", None) or "tool"
        args = _tool_args(item)
        console.print(f"[cyan]→ {name}[/]", end=" " if args else "\n")
        if args:
            console.print(args, style="dim", markup=False, highlight=False)

    def _tool_output(self, output) -> None:
        self._thinking = False
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


def _tool_args(item) -> str:
    raw = getattr(item, "raw_item", None)
    if isinstance(raw, dict):
        return raw.get("arguments") or ""
    return getattr(raw, "arguments", None) or ""


def _format_tokens(usage, context_length: int) -> str:
    if usage.request_usage_entries:
        last = usage.request_usage_entries[-1]
        used = last.total_tokens
    else:
        used = usage.total_tokens
    pct = (used / context_length * 100) if context_length else 0
    return f"{used:,} / {context_length:,} tokens ({pct:.0f}%)"


if __name__ == "__main__":
    main()
