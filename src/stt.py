from llm import get_client
from settings import settings


def transcribe_file(path: str) -> str:
    with open(path, "rb") as audio_file:
        transcript = get_client().audio.transcriptions.create(
            model=settings.stt_model,
            file=audio_file,
            language=settings.stt_language,
        )
    return transcript.text