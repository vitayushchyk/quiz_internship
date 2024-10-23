FROM python:3.12-slim AS base

ARG APP_ENV
ENV APP_ENV=${APP_ENV:-development} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.7.1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  SERVER_PORT=8080

RUN apt-get update \
    && apt-get install --no-install-recommends -y libpq-dev \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==$POETRY_VERSION"

RUN mkdir /app

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock ./README.md /app/
RUN  poetry install --no-root --only main


FROM base AS prod

COPY . .

CMD ["bash", "-c", "uvicorn main:app --host 0.0.0.0 --port $SERVER_PORT"]


FROM base AS dev

RUN  poetry install --no-root

COPY . .

CMD ["bash", "-c", "uvicorn main:app --host 0.0.0.0 --port $SERVER_PORT --reload"]


FROM dev AS test

CMD ["bash", "-c", "pytest"]
