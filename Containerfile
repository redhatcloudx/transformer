FROM python:3.11-alpine

COPY ./dist/*.whl /opt/cloudimagedirectory/
COPY ./data/image-data.json /opt/cloudimagedirectory/
WORKDIR /opt/cloudimagedirectory

RUN apk update \
    && apk --no-cache --update add build-base

RUN pip install ./*.whl

CMD ["cloudimagedirectory-updater", "serve", "--file-path", "/opt/cloudimagedirectory/image-data.json"]
