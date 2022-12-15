FROM python:3.10-alpine

COPY ./dist/*.whl /opt/rhelocator/
COPY ./data/image-data.json /opt/rhelocator/
WORKDIR /opt/rhelocator

RUN apk update \
    && apk --no-cache --update add build-base

RUN pip install ./*.whl

CMD ["rhelocator-updater", "serve", "--file-path", "/opt/rhelocator/image-data.json"]
