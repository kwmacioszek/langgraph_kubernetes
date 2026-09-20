from pathlib import Path

from llm import get_client
from settings import settings


def synthesize_file(text: str, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    speech = get_client().audio.speech.create(
        model=settings.tts_model,
        voice=settings.tts_voice,
        input=text,
        response_format="mp3",
    )
    out_path.write_bytes(speech.content)
    return out_path
