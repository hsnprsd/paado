from typing import Protocol

import requests
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel

from config import Config


class Provider(Protocol):
    def model(self, name: str) -> Agent: ...
    def list_available_models(self) -> list[str]: ...


class OllamaProvider:
    def __init__(self, config: Config):
        self.host = config.ollama_host.rstrip("/")

    def model(self, name: str) -> Agent:
        return Agent(
            name="Assistant",
            instructions="Complete the user's task.",
            model=OpenAIChatCompletionsModel(
                model=name,
                openai_client=AsyncOpenAI(
                    base_url=f"{self.host}/v1",
                    api_key="ollama",
                ),
            ),
        )

    def list_available_models(self) -> list[str]:
        resp = requests.get(f"{self.host}/api/tags")
        resp.raise_for_status()
        return [m["name"] for m in resp.json()["models"]]
