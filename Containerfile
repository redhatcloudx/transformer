FROM python:3.10-alpine

COPY ./dist/*.whl /opt/cloud-image-directory/
COPY ./data/image-data.json /opt/cloud-image-directory/
WORKDIR /opt/cloud-image-directory

RUN apk update \
    && apk --no-cache --update add build-base

RUN pip install ./*.whl

CMD ["cloud-image-directory-updater", "serve", "--file-path", "/opt/cloud-image-directory/image-data.json"]
