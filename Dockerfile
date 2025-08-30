FROM ghcr.io/astral-sh/uv:debian

WORKDIR /app

COPY pyproject.toml uv.lock* ./

ENV UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    (uv sync --locked --no-install-project || uv sync --no-install-project)

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    (uv sync --locked || uv sync)

RUN uv tool install . --force --editable

ENV PATH="/usr/local/bin:/app/.venv/bin:${PATH}"

EXPOSE 5000

CMD ["imagez_web"]
