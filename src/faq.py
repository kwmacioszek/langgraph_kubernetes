import re
from functools import lru_cache

from settings import settings


@lru_cache(maxsize=1)
def load_faq() -> dict[str, str]:
    """Parsuje data/faq.md na słownik {kategoria: tekst sekcji}.

    Nagłówki mają format `## <kategoria> — <pytanie>` — kategoria musi być jedną
    z wartości `schemas.Category`, żeby classify_intent mógł na nią trafić.
    """
    text = settings.faq_path.read_text(encoding="utf-8")
    faq: dict[str, str] = {}
    for header, body in re.findall(
        r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", text, flags=re.MULTILINE | re.DOTALL
    ):
        slug = header.split("—", 1)[0].strip()
        faq[slug] = f"{header.strip()}\n{body.strip()}"
    return faq


def get_answer_text(category: str) -> str | None:
    return load_faq().get(category)