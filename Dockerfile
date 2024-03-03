FROM python:3.11
ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

RUN pip install poetry
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
  && poetry install --without=dev --no-interaction --no-ansi --no-root
# requirements should not be reinstalled on every rebuild
COPY ./src/ ./.env ./
CMD ["poetry", "run", "python", "main.py"]
