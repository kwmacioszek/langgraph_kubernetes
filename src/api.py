import logging
import os
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, UploadFile
from pydantic import BaseModel

from settings import settings

logging.basicConfig(
    level=logging.INFO
)  # żeby log_transcript_node (graph.py) było widać w konsoli

if settings.langsmith_tracing:
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint

from graph import build_graph

app = FastAPI(title="Voice bot bankowy", version="0.1.0")
compiled_graph = build_graph()


class VoiceResponse(BaseModel):
    raw_transcript: str
    category: str
    question: str
    answer: str
    escalated: bool


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/voice")
def voice(file: UploadFile) -> VoiceResponse:
    """Transkrybuje nagranie i przechodzi cały graf: log transkrypcji -> klasyfikacja -> FAQ/konsultant."""
    uploads = Path(settings.uploads_dir)
    uploads.mkdir(parents=True, exist_ok=True)
    path = uploads / f"{uuid4().hex}{Path(file.filename or '').suffix}"
    with path.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    result = compiled_graph.invoke({"audio_path": str(path)})

    return VoiceResponse(
        raw_transcript=result["raw_transcript"],
        category=result["intent"].category,
        question=result["intent"].question,
        answer=result["answer"],
        escalated=result["escalated"],
    )
