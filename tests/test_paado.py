import asyncio

from config import Config
from loop import Loop
from paado import Paado
from providers import OllamaProvider


def test_paado_smoke():
    config = Config()
    provider = OllamaProvider(config)
    models = provider.list_available_models()
    assert models, "no ollama models available"

    asyncio.run(_search_hello_world(config, provider.model(models[0])))


async def _search_hello_world(config, agent):
    paado = Paado(config, agent)
    await paado.start()
    try:
        result = await Loop(paado.agent).run(
            "Open en.wikipedia.org and search for hello world."
        )
        assert result
        url = paado.browser.page.url.lower()
        html = await paado.browser.do_read_html()
        assert "google." in url
        assert "hello" in html.lower() and "world" in html.lower()
    finally:
        await paado.close()
