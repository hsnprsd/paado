import asyncio

from config import Config
from loop import Loop
from providers import OllamaProvider


def test_loop_smoke():
    config = Config()
    provider = OllamaProvider(config)
    models = provider.list_available_models()
    assert models, "no ollama models available"

    result = asyncio.run(Loop(provider.model(models[0])).run("Reply with the single word: ok"))

    assert result
    assert "ok" in result.lower()
