from pydantic_settings import BaseSettings


class Config(BaseSettings):
    ollama_host: str = "http://127.0.0.1:11434"
    chrome_path: str = "/usr/bin/google-chrome"
    chrome_headless: bool = False
