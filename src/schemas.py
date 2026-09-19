from typing import Literal

from pydantic import BaseModel, Field

Category = Literal[
    "pin",
    "reklamacja",
    "oplaty",
    "karta",
    "godziny",
    "wyciagi",
    "nowe_konto",
    "limity",
    "consultant",
]



class Intent(BaseModel):
    """Wyjście węzła `classify_intent`."""

    category: Category = Field(
        description="Kategoria FAQ najlepiej opisująca pytanie, albo 'consultant'"
    )
    question: str = Field(
        description="Właściwe pytanie klienta, oczyszczone z podziękowań/wstępów"
    )
    confidence: float = Field(ge=0.0, le=1.0)


class GraphState(BaseModel):
    """Stan przepływający między węzłami LangGraph — walidowany pydantic, nie gołe dict/TypedDict."""

    audio_path: str
    raw_transcript: str = ""
    intent: Intent | None = None
    answer: str = ""
    escalated: bool = False


class FaqAnswer(BaseModel):
    """Wyjście węzła `faq_answer` — model tylko przeformułowuje ustalony tekst FAQ."""

    answer: str = Field(
        description="Odpowiedź po polsku, oparta wyłącznie na tekście FAQ dla danej kategorii"
    )
    found: bool = Field(
        description="False, jeśli tekst FAQ dla tej kategorii nie odpowiada na pytanie"
    )