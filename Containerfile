FROM python:3.10-alpine

COPY . /opt/rhelocator/
WORKDIR /opt/rhelocator

RUN apk update \
    && apk --no-cache --update add build-base

ENV POETRY_VERSION=1.2.1

RUN pip install "poetry==$POETRY_VERSION"

RUN poetry config virtualenvs.create false
RUN poetry install --only main --no-interaction --no-ansi

# TODO: Implement API backend + add cli command to run and configure API
# EXPOSE 8000
# CMD ["poetry", "run", "rhelocator-cli", "serve", "--image-data", "/path/to/image/data.json"]
