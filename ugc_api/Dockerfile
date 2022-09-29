FROM python:3.9.6-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ARG DEV_DEPS=False

RUN apt-get update \
    && apt-get  install -y --no-install-recommends gcc python3-dev musl-dev bash libpq-dev

RUN python -m pip install --upgrade pip poetry

COPY pyproject.toml ./poetry.lock ./
RUN poetry config virtualenvs.create false

RUN if [ $DEV_DEPS = True ] ; then \
    poetry install --no-interaction --no-ansi ; else \
    poetry install --no-dev --no-interaction --no-ansi ; fi

WORKDIR /app
COPY . .
EXPOSE 8080
CMD gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
