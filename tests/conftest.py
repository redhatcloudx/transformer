"""Configuration for tests."""
from __future__ import annotations

import pytest


MOCKED_AWS_IMAGE_LIST = [
    {"ImageId": "ami-0001", "UsageOperation": "RunInstances:0010"},
    {"ImageId": "ami-0002", "UsageOperation": "RunInstances:0010"},
    {"ImageId": "ami-0003", "UsageOperation": "RunInstances:0000"},
]

MOCKED_AZURE_IMAGE_VERSION_LIST = [
    "9.0.2022053014",
    "9.0.2022062014",
    "9.0.2022062414",
    "9.0.2022081801",
    "9.0.2022090601",
]

MOCKED_GCP_IMAGE_LIST = [
    "rhel-7-v20220920",
    "rhel-8-v20220920",
    "rhel-9-arm64-v20220920",
    "rhel-9-v20220920",
]


def pytest_configure(config: any) -> None:
    config.addinivalue_line("markers", "e2e: mark as end-to-end test.")


@pytest.fixture
def mock_aws_regions(mocker):
    """Provide an offline result for calls to get_aws_regions."""
    mock = mocker.patch("rhelocator.update_images.aws.get_aws_regions")
    mock.return_value = ["us-east-1", "us-east-2"]
    return mock


@pytest.fixture
def mock_aws_images(mocker):
    """Provide an offline result for calls to get_aws_images."""
    mock = mocker.patch("rhelocator.update_images.aws.aws_describe_images")
    mock.return_value = MOCKED_AWS_IMAGE_LIST
    return mock


@pytest.fixture
def mock_azure_image_versions(mocker):
    """Provide an offline result got get_azure_image_versions."""
    mock = mocker.patch("rhelocator.update_images.azure.get_azure_image_versions")
    mock.return_value = MOCKED_AZURE_IMAGE_VERSION_LIST
    return mock


@pytest.fixture
def mock_azure_image_versions_latest(mocker):
    """Provide an offline result got get_azure_image_versions."""
    mock = mocker.patch("rhelocator.update_images.azure.get_azure_image_versions")
    mock.return_value = [MOCKED_AZURE_IMAGE_VERSION_LIST[0]]
    return mock


@pytest.fixture
def mock_gcp_images(mocker):
    """Provide an offline result for calls to get_google_images."""
    mock = mocker.patch("rhelocator.update_images.gcp.get_google_images")
    mock.return_value = MOCKED_GCP_IMAGE_LIST
    return mock