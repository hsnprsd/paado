from pydantic_settings import BaseSettings


class Config(BaseSettings):
    ollama_host: str = "http://127.0.0.1:11434"
    context_length: int = 64 * 1024
    chrome_path: str = "/usr/bin/google-chrome"
    chrome_headless: bool = False
