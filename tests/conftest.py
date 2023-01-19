"""Configuration for tests."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest


MOCKED_AWS_IMAGE_LIST = [
    {
        "ImageId": "ami-0001",
        "UsageOperation": "RunInstances:0010",
        "Architecture": "x86_64",
        "CreationDate": "2021-02-10T16:19:48.000Z",
        "Name": "RHEL-8.3_HVM-20210209-x86_64-0-Hourly2-GP2",
        "VirtualizationType": "hvm",
    },
    {
        "ImageId": "ami-0002",
        "UsageOperation": "RunInstances:0010",
        "Architecture": "x86_64",
        "CreationDate": "2021-02-10T16:19:48.000Z",
        "Name": "RHEL-8.3_HVM-20210209-x86_64-0-Hourly2-GP2",
        "VirtualizationType": "hvm",
    },
    {
        "ImageId": "ami-0003",
        "UsageOperation": "RunInstances:0000",
        "Architecture": "x86_64",
        "CreationDate": "2021-02-10T16:19:48.000Z",
        "Name": "RHEL-8.3_HVM-20210209-x86_64-0-Access2-GP2",
        "VirtualizationType": "hvm",
    },
]

MOCKED_AZURE_IMAGE_LIST = [
    {
        "architecture": "x86_64",
        "hyperVGeneration": "v2",
        "offer": "offer",
        "publisher": "publisher",
        "sku": "sku",
        "urn": "publisher:offer:sku:9.0.2022053014",
        "version": "9.0.2022053014",
    },
    {
        "architecture": "x86_64",
        "hyperVGeneration": "v2",
        "offer": "offer",
        "publisher": "publisher",
        "sku": "sku",
        "urn": "publisher:offer:sku:9.0.2022062014",
        "version": "9.0.2022062014",
    },
    {
        "architecture": "x86_64",
        "hyperVGeneration": "v2",
        "offer": "offer",
        "publisher": "publisher",
        "sku": "sku",
        "urn": "publisher:offer:sku:9.0.2022062414",
        "version": "9.0.2022062414",
    },
]

MOCKED_AZURE_IMAGE_VERSION_LIST = [
    "9.0.2022053014",
    "9.0.2022062014",
    "9.0.2022062414",
    "9.0.2022081801",
    "9.0.2022090601",
]

MOCKED_AZURE_IMAGE_DETAILS = {
    "properties": {
        "architecture": "x64",
        "hyperVGeneration": "V2",
    }
}

MOCKED_AZURE_ACCESS_TOKEN = "access_token"

def pytest_configure(config: any) -> None:
    config.addinivalue_line("markers", "e2e: mark as end-to-end test.")


@pytest.fixture
def mock_aws_regions(mocker):
    """Provide an offline result for calls to get_aws_regions."""
    mock = mocker.patch("rhelocator.update_images.aws.get_regions")
    mock.return_value = ["us-east-1", "us-east-2"]
    return mock


@pytest.fixture
def mock_aws_images(mocker):
    """Provide an offline result for calls to get_aws_images."""
    mock = mocker.patch("rhelocator.update_images.aws.describe_images")
    mock.return_value = MOCKED_AWS_IMAGE_LIST
    return mock

@pytest.fixture
def mock_azure_access_token(mocker):
    """Provide an offline result got get_azure_image_versions."""
    mock = mocker.patch("rhelocator.update_images.azure.get_access_token")
    mock.return_value = MOCKED_AZURE_ACCESS_TOKEN
    return mock


@pytest.fixture
def mock_azure_image_versions(mocker):
    """Provide an offline result got get_azure_image_versions."""
    mock = mocker.patch("rhelocator.update_images.azure.get_image_versions")
    mock.return_value = MOCKED_AZURE_IMAGE_VERSION_LIST
    return mock


@pytest.fixture
def mock_azure_image_versions_latest(mocker):
    """Provide an offline result got get_azure_image_versions."""
    mock = mocker.patch("rhelocator.update_images.azure.get_image_versions")
    mock.return_value = [MOCKED_AZURE_IMAGE_VERSION_LIST[0]]
    return mock


@pytest.fixture
def mock_azure_image_details(mocker):
    """Provide an offline result got get_azure_image_details."""
    mock = mocker.patch("rhelocator.update_images.azure.get_image_details")
    mock.return_value = MOCKED_AZURE_IMAGE_DETAILS
    return mock


@pytest.fixture
def mock_azure_images(mocker):
    """Provide an offline result for calls to azure.get_images."""
    mock = mocker.patch("rhelocator.update_images.azure.get_images")
    mock.return_value = MOCKED_AZURE_IMAGE_LIST
    return mock


@pytest.fixture
def mock_google_images(mocker):
    """Provide an offline result for calls to get_google_images."""
    mock = mocker.patch("rhelocator.update_images.google.get_images")

    mocked_image = {
        "id": "rhel-7-9-sap-v20220719",
        "architecture": "x86_64",
        "creation_timestamp": "2022-09-20T16:32:45.572-07:00",
        "description": "Red Hat, Red Hat Enterprise Linux, 7, x86_64",
        "name": "rhel-7-v20220920",
    }
    mock.return_value = [mocked_image]

    return mock


@pytest.fixture
def mock_normalize_google_images(mocker):
    """Provide an offline result for calls to normalize_google_images."""
    mock = mocker.patch("rhelocator.update_images.google.normalize_google_images")

    # Fake a Google image listing.
    mocked_image = MagicMock()
    mocked_image.architecture = "X86_64"
    mocked_image.creation_timestamp = "20221018"
    mocked_image.description = "RHEL"
    mocked_image.name = "rhel-9-20221018"
    mock.return_value = [mocked_image]

    return mock
