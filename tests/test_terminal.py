import asyncio

from config import Config
from loop import Loop
from paado import Paado
from plugins.terminal import TerminalPlugin
from providers import OllamaProvider
from terminal import TerminalSession


def test_terminal_exec():
    asyncio.run(_exec_echo())


async def _exec_echo():
    session = TerminalSession(Config())
    await session.start()
    try:
        output = await session.do_exec("echo hello")
        assert "hello" in output
        assert "exit code: 0" in output
    finally:
        await session.close()


def test_terminal_smoke():
    config = Config()
    provider = OllamaProvider(config)
    models = provider.list_available_models()
    assert models, "no ollama models available"

    asyncio.run(_run_echo_script(config, provider.model(models[0])))


async def _run_echo_script(config, agent):
    plugin = TerminalPlugin(config)
    paado = Paado(agent, plugins=[plugin])
    await paado.start()
    try:
        result = await Loop(paado.agent).run(
            "Execute a bash script that prints the exact text: hello-from-paado"
        )
        assert result
        assert "hello-from-paado" in result.lower()
    finally:
        await paado.close()
