"""Serve image data from public clouds."""
from __future__ import annotations

import json

import pytest
from flask import Flask
from flask_cors import CORS
from rhelocator.api.routes.health import health_blueprint

from rhelocator.api import server


@pytest.fixture()
def app():
    app = server.create_app("tests/api/testdata/formatted_images.json")
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def empty_app():
    empty_app = Flask(__name__)

    empty_app.register_blueprint(
        health_blueprint({}), url_prefix="/api"
    )

    yield empty_app


@pytest.fixture()
def corrupted_client(empty_app):
    return empty_app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_request_google(client):
    response = client.get("/api/google")
    assert len(response.data) > 0
    assert response.status_code == 200


def test_request_google_with_query(client):
    response = client.get(
        "/api/google",
        query_string={
            "version": "9",
        },
    )
    for image in json.loads(response.data):
        assert image["version"] == "9"
    assert response.status_code == 200


def test_request_google_with_multi_query(client):
    test_query = {
        "name": "RHEL 9",
        "arch": "arm64",
        "version": "9",
        "imageId": "rhel-9",
        "date": "2022-11-02",
    }
    response = client.get("/api/google", query_string=test_query)
    for image in json.loads(response.data):
        assert test_query["name"] in image["name"]
        assert test_query["arch"] in image["arch"]
        assert test_query["version"] in image["version"]
        assert test_query["imageId"] in image["imageId"]
        assert test_query["date"] in image["date"]
    assert response.status_code == 200


def test_request_aws(client):
    response = client.get("/api/aws")
    assert len(response.data) > 0
    assert response.status_code == 200


def test_request_aws_with_query(client):
    response = client.get(
        "/api/aws",
        query_string={
            "version": "8.1.0",
        },
    )
    for image in json.loads(response.data):
        assert image["version"] == "8.1.0"
    assert response.status_code == 200


def test_request_aws_with_multi_query(client):
    test_query = {
        "name": "RHEL-8.1.0",
        "arch": "x86_64",
        "version": "8.1.0",
        "imageId": "ami-0bcadaece3162039d",
        "date": "2022-09-06",
        "virt": "HVM",
        "region": "us-east-1",
    }
    response = client.get("/api/aws", query_string=test_query)
    for image in json.loads(response.data):
        assert test_query["name"] in image["name"]
        assert test_query["arch"] in image["arch"]
        assert test_query["version"] in image["version"]
        assert test_query["imageId"] in image["imageId"]
        assert test_query["date"] in image["date"]
        assert test_query["virt"] in image["virt"]
        assert test_query["region"] in image["region"]
    assert response.status_code == 200


def test_request_azure(client):
    response = client.get("/api/azure")
    assert response.status_code == 200


def test_request_azure_with_query(client):
    response = client.get(
        "/api/azure",
        query_string={
            "version": "9.0",
        },
    )
    for image in json.loads(response.data):
        assert image["version"] == "9.0"
    assert response.status_code == 200


def test_request_azure_with_multi_query(client):
    test_query = {
        "name": "RHEL 9-lvm-gen2 x64",
        "arch": "x64",
        "version": "9.0",
        "imageId": "redhat:RHEL:9-lvm-gen2:9.0.2022090601",
        "date": "2022-09-06",
        "virt": "V2",
    }
    response = client.get("/api/azure", query_string=test_query)
    for image in json.loads(response.data):
        assert test_query["name"] in image["name"]
        assert test_query["arch"] in image["arch"]
        assert test_query["version"] in image["version"]
        assert test_query["imageId"] in image["imageId"]
        assert test_query["date"] in image["date"]
        assert test_query["virt"] in image["virt"]
    assert response.status_code == 200


def test_request_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200


def test_request_health_with_corrupt_data(corrupted_client):
    response = corrupted_client.get("/api/health")
    assert response.status_code == 500