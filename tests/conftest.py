"""Configuration for tests."""
from __future__ import annotations

import pytest


MOCKED_AWS_IMAGE_LIST = [
    {"ImageId": "ami-0001", "UsageOperation": "RunInstances:0010"},
    {"ImageId": "ami-0002", "UsageOperation": "RunInstances:0010"},
    {"ImageId": "ami-0003", "UsageOperation": "RunInstances:0000"},
]


def pytest_configure(config: any) -> None:
    config.addinivalue_line("markers", "e2e: mark as end-to-end test.")


@pytest.fixture
def mock_aws_regions(mocker):
    """Provide an offline result for calls to get_aws_regions."""
    mock = mocker.patch("rhelocator.update_images.get_aws_regions")
    mock.return_value = ["us-east-1", "us-east-2"]
    return mock


@pytest.fixture
def mock_aws_images(mocker):
    """Provide an offline result for calls to get_aws_images."""
    mock = mocker.patch("rhelocator.update_images.aws_describe_images")
    mock.return_value = MOCKED_AWS_IMAGE_LIST
    return mock
