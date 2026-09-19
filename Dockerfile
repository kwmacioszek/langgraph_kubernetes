FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.12 /uv /bin/uv

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never

# Najpierw same zależności (bez src/) — warstwa z cache, nie przebudowuje się przy zmianie kodu.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --no-dev --no-install-project

COPY src ./src
COPY data/faq.md ./data/faq.md

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8020
CMD ["uvicorn", "api:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8020"]
