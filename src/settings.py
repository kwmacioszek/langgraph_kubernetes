from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    stt_model: str = "whisper-1"
    stt_language: str = "pl"
    tts_model: str = "gpt-4o-mini-tts"
    tts_voice: str = "alloy"

    model_config = SettingsConfigDict(env_file=".env")

    model_name: str = "gpt-4o-mini"
    faq_path: Path = Path("data/faq.md")

    langsmith_tracing: bool = False  # LANGSMITH_TRACING
    langsmith_api_key: str = ""  # LANGSMITH_API_KEY
    langsmith_project: str = "voice-bank-bot"  # LANGSMITH_PROJECT
    langsmith_endpoint: str = ""  # LANGSMITH_ENDPOINT

    uploads_dir: Path = Path("data/uploads")
    replies_dir: Path = Path(
        "data/uploads/replies"
    ) 


settings = Settings()