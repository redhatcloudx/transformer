"""Test image updates from remote cloud APIs."""
from __future__ import annotations

import pytest

from jsonschema import ValidationError

from cloudimagedirectory.update_images import schema


def test_valid_image_data_validation():
    """Test image data validation with valid input."""
    image_data = {
        "images": {
            "aws": [
                {
                    "name": "some name",
                    "arch": "some arch",
                    "version": "some version",
                    "imageId": "some id",
                    "date": "some date",
                    "virt": "some virt",
                    "selflink": "https://console.aws.amazon.com/ec2/home?region=eu-north-1#launchAmi=ami-0e02b69290bcd7b69",  # noqa: E501
                    "region": "some region",
                }
            ],
            "azure": [
                {
                    "name": "some name",
                    "arch": "some arch",
                    "version": "some version",
                    "imageId": "some id",
                    "date": "some date",
                    "virt": "some virt",
                }
            ],
            "google": [
                {
                    "name": "some name",
                    "arch": "some arch",
                    "version": "some version",
                    "imageId": "some id",
                    "date": "some date",
                    "virt": "some virt",
                    "selflink": "https://console.cloud.google.com/compute/imagesDetail/projects/rhel-cloud/global/images/rhel-7-v20220719",  # noqa: E501
                }
            ],
        }
    }

    try:
        schema.validate_json(image_data)
    except ValidationError as exc:
        raise AssertionError(f"Validating proper image data raised an exception! {exc}")


def test_incomplete_image_data_validation():
    """Test image data validation with incomplete input."""
    image_data = {
        "images": {
            "aws": [
                {
                    "name": "some name",
                    "arch": "some arch",
                    "version": "some version",
                    "imageId": "some id",
                    "virt": "some virt",
                    "selflink": "https://console.aws.amazon.com/ec2/home?region=eu-north-1#launchAmi=ami-0e02b69290bcd7b69",  # noqa: E501
                    "region": "some region",
                }
            ]
        }
    }

    with pytest.raises(ValidationError, match=r".*'date' is a required property.*"):
        schema.validate_json(image_data)


def test_invalid_image_data_validation():
    """Test image data validation with invalid input type."""
    image_data = {
        "images": {
            "aws": [
                {
                    "name": "some name",
                    "arch": "some arch",
                    "version": False,
                    "imageId": "some id",
                    "virt": "some virt",
                    "date": "some date",
                    "selflink": "https://console.aws.amazon.com/ec2/home?region=eu-north-1#launchAmi=ami-0e02b69290bcd7b69",  # noqa: E501
                    "region": "some region",
                }
            ]
        }
    }

    with pytest.raises(ValidationError, match=r".*False is not of type 'string'*"):
        schema.validate_json(image_data)


def test_invalid_extra_image_data_validation():
    """Test image data validation with invalid extrea input data."""
    image_data = {
        "images": {
            "oracle": [
                {
                    "name": "some name",
                    "arch": "some arch",
                    "version": "some version",
                    "imageId": "some id",
                    "virt": "some virt",
                    "date": "some date",
                    "selflink": "https://console.aws.amazon.com/ec2/home?region=eu-north-1#launchAmi=ami-0e02b69290bcd7b69",  # noqa: E501
                    "region": "some region",
                }
            ]
        }
    }

    with pytest.raises(
        ValidationError, match=r".*Additional properties are not allowed*"
    ):
        schema.validate_json(image_data)


def test_malicious_url():
    """Test image data validation with malicious url injection."""
    image_data = {
        "images": {
            "aws": [
                {
                    "name": "some name",
                    "arch": "some arch",
                    "version": "some version",
                    "imageId": "some id",
                    "virt": "some virt",
                    "date": "some date",
                    "selflink": "http://some-evil-url.com/?https://console.aws.amazon.com/ec2/home?region=eu-north-1#launchAmi=ami-0e02b69290bcd7b69",  # noqa: E501
                    "region": "some region",
                }
            ]
        }
    }

    with pytest.raises(ValidationError, match=r".*does not match*"):
        schema.validate_json(image_data)
