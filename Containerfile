FROM python:3.10-alpine

COPY . /opt/rhelocator/
WORKDIR /opt/rhelocator

RUN apk update \
    && apk --no-cache --update add build-base

ENV POETRY_VERSION=1.2.1

RUN pip install "poetry==$POETRY_VERSION"

RUN poetry config virtualenvs.create false
RUN poetry install --only main --no-interaction --no-ansi

CMD ["poetry", "run", "rhelocator-updater", "serve", "--file-path", "/opt/rhelocator/data/image-data.json"]
