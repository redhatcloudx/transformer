FROM registry.access.redhat.com/ubi9/ubi:latest

COPY ./dist/*.whl /opt/rhelocator/
COPY ./data/image-data.json /opt/rhelocator/
WORKDIR /opt/rhelocator

RUN dnf -y install pip && dnf clean all

RUN pip install ./*.whl

CMD ["rhelocator-updater", "serve", "--file-path", "/opt/rhelocator/image-data.json"]
