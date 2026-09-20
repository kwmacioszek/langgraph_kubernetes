import argparse
import json
import logging
import os

from settings import settings

logging.basicConfig(level=logging.INFO)


from graph import build_graph

if settings.langsmith_tracing:
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Przepuszcza nagranie audio przez graf voice-bank-bot."
    )
    parser.add_argument(
        "audio_path", help="Ścieżka do pliku audio (wav, mp3, m4a, ...)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Wypisz wynik jako JSON zamiast czytelnego tekstu",
    )
    args = parser.parse_args()

    compiled_graph = build_graph()
    result = compiled_graph.invoke({"audio_path": args.audio_path})

    if args.json:
        print(
            json.dumps(
                {
                    "raw_transcript": result["raw_transcript"],
                    "category": result["intent"].category,
                    "question": result["intent"].question,
                    "answer": result["answer"],
                    "escalated": result["escalated"],
                    "answer_audio_path": result["answer_audio_path"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    print(f"Transkrypcja: {result['raw_transcript']}")
    print(f"Kategoria:    {result['intent'].category}")
    print(f"Pytanie:      {result['intent'].question}")
    print(f"Odpowiedź:    {result['answer']}")
    print(f"Eskalacja:    {result['escalated']}")
    print(f"Ścieżka do odpowiedzi audio: {result['answer_audio_path']}")


if __name__ == "__main__":
    main()