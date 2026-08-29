import argparse
import asyncio
import sys

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
            await _run_task(paado, task)
            return
        await _repl(paado)
    finally:
        await paado.close()


async def _run_task(paado: Paado, task: str) -> None:
    with console.status("Working..."):
        result = await Loop(paado.agent).run(task)
    if result:
        console.print(Markdown(str(result)))


async def _repl(paado: Paado) -> None:
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
        await _run_task(paado, task)


if __name__ == "__main__":
    main()
