from typing import Protocol

from agents import Agent, AsyncOpenAI, ModelSettings, OpenAIChatCompletionsModel

from config import Config


class Provider(Protocol):
    def model(self, name: str) -> Agent: ...


class OllamaProvider:
    def __init__(self, config: Config):
        self.host = config.ollama_host.rstrip("/")
        self.context_length = config.context_length
        self.thinking_effort = config.thinking_effort

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
            model_settings=ModelSettings(
                extra_body={
                    "options": {"num_ctx": self.context_length},
                    "think": (
                        False if self.thinking_effort == "none" else self.thinking_effort
                    ),
                },
            ),
        )
