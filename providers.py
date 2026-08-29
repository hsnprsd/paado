from typing import Protocol

import requests

from config import Config


class Model(Protocol):
    def generate(self, prompt: str) -> str: ...


class Provider(Protocol):
    def model(self, name: str) -> Model: ...
    def list_available_models(self) -> list[str]: ...


class OllamaModel:
    def __init__(self, name: str, host: str):
        self.name = name
        self.host = host

    def generate(self, prompt: str) -> str:
        resp = requests.post(
            f"{self.host}/api/generate",
            json={"model": self.name, "prompt": prompt, "stream": False},
        )
        resp.raise_for_status()
        return resp.json()["response"]


class OllamaProvider:
    def __init__(self, config: Config):
        self.host = config.ollama_host.rstrip("/")

    def model(self, name: str) -> OllamaModel:
        return OllamaModel(name, self.host)

    def list_available_models(self) -> list[str]:
        resp = requests.get(f"{self.host}/api/tags")
        resp.raise_for_status()
        return [m["name"] for m in resp.json()["models"]]
