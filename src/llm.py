from functools import lru_cache

from langsmith.wrappers import wrap_openai
from openai import OpenAI

from schemas import Intent
from settings import settings

from faq import get_answer_text
from schemas import FaqAnswer


CLASSIFY_PROMPT = """Klasyfikujesz zapytania klientów banku do jednej z kategorii FAQ:
- pin: reset/zmiana PIN-u do karty
- reklamacja: reklamacja nierozpoznanej transakcji
- oplaty: opłaty za przelewy
- karta: zastrzeżenie zgubionej/skradzionej karty
- godziny: godziny obsługi klienta
- wyciagi: wyciąg z konta
- nowe_konto: dokumenty do otwarcia nowego konta
- limity: zmiana limitu transakcji na karcie
- consultant: wszystko inne — sprawy wymagające dostępu do konkretnego konta,
  spory, niestandardowe przypadki, albo gdy klient wprost prosi o człowieka

Wypisz też oczyszczone pytanie klienta (bez wstępów/podziękowań)."""

ANSWER_PROMPT = """Odpowiadasz klientowi banku po polsku, wyłącznie na podstawie podanego tekstu FAQ.
Przeformułuj go tak, żeby bezpośrednio odpowiadał na pytanie klienta. Jeśli tekst FAQ nie odpowiada
na to pytanie, ustaw found=false i nie zgaduj."""


@lru_cache(maxsize=1)
def get_client() -> OpenAI:
    return wrap_openai(OpenAI(api_key=settings.openai_api_key))


def classify_intent(text: str) -> Intent:
    completion = get_client().chat.completions.parse(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": CLASSIFY_PROMPT},
            {"role": "user", "content": text},
        ],
        response_format=Intent,
        temperature=0,
    )
    return completion.choices[0].message.parsed


def answer_faq(category: str, question: str) -> FaqAnswer:
    faq_text = get_answer_text(category)
    if faq_text is None:
        return FaqAnswer(answer="", found=False)
    completion = get_client().chat.completions.parse(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": ANSWER_PROMPT},
            {
                "role": "user",
                "content": f"Pytanie: {question}\n\nTekst FAQ:\n{faq_text}",
            },
        ],
        response_format=FaqAnswer,
        temperature=0,
    )
    return completion.choices[0].message.parsed