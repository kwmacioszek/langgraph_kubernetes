import logging
import os
import shutil
from pathlib import Path
from uuid import uuid4
import tempfile

from fastapi import FastAPI, UploadFile, Response
from pydantic import BaseModel
from faq import load_faq

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


@app.get("/ready")
def ready(response: Response) -> dict[str, object]:
    """Readiness: czy ten pod potrafi obsłużyć POST /voice. 503 = K8s wyjmuje go z Service."""
    failed = []
    try:
        if not load_faq():
            failed.append("faq")
    except OSError:
        failed.append("faq")
    if not settings.openai_api_key:
        failed.append("openai_api_key")
    try:
        Path(settings.uploads_dir).mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=settings.uploads_dir):
            pass
    except OSError:
        failed.append("uploads")

    if failed:
        response.status_code = 503
    return {"status": "not ready" if failed else "ready", "failed": failed}


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
