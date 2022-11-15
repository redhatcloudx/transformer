"""Test image updates from remote cloud APIs."""
from __future__ import annotations

from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

from jsonschema import ValidationError

from rhelocator.update_images import gcp
from rhelocator.update_images import schema


@patch("rhelocator.update_images.gcp.compute_v1.ImagesClient")
def test_get_images(mock_gcp: MagicMock) -> None:
    """Test getting Google images."""
    # Fake a valid, non-deprecated image.
    mock_image = Mock()
    mock_image.name = "valid_image"

    # Fake a deprecated Google image listing.
    mocked_deprecated_image = MagicMock()
    mocked_deprecated_image.architecture = "X86_64"
    mocked_deprecated_image.creation_timestamp = "19750101"
    mocked_deprecated_image.description = "RHEL"
    mocked_deprecated_image.name = "rhel-0-19750101"
    mocked_deprecated_image.deprecated.state = "DEPRECATED"

    # Fake a valid Google image listing.
    mocked_valid_image = MagicMock()
    mocked_valid_image.architecture = "X86_64"
    mocked_valid_image.creation_timestamp = "20221018"
    mocked_valid_image.description = "RHEL"
    mocked_valid_image.name = "rhel-9-20221018"

    # Connect the mock to the ImagesClient return value.
    mock_response = MagicMock()
    mock_response.list.return_value = [mocked_valid_image, mocked_deprecated_image]
    mock_gcp.return_value = mock_response

    images = gcp.get_images()
    assert len(images) == 1


def test_normalize_google_images() -> None:
    """Test normalizing Google image data."""
    # Fake a Google image listing.
    mocked_image = MagicMock()
    mocked_image.architecture = "X86_64"
    mocked_image.creation_timestamp = "20221018"
    mocked_image.description = "RHEL"
    mocked_image.name = "rhel-9-20221018"

    images = gcp.normalize_google_images([mocked_image])

    assert isinstance(images, list)
    assert images[0] == {
        "architecture": "x86_64",
        "creation_timestamp": "20221018",
        "description": "RHEL",
        "name": "rhel-9-20221018",
    }


def test_parse_image_version_from_name():
    """Test parsing a google image name with a basic image."""
    image_name = "rhel-7-9-sap-v20220719"
    version = gcp.parse_image_version_from_name(image_name)

    assert version == "7.9"

    """Test parsing a google image name with a basic image."""
    image_name = "rhel-7-sap-v20220719"
    version = gcp.parse_image_version_from_name(image_name)

    assert version == "7"

    """Test parsing a google image name with a basic image."""
    image_name = "rhel-7-1-2-sap-v20220719"
    version = gcp.parse_image_version_from_name(image_name)

    assert version == "7.1.2"

    """Test parsing a google image name with a basic image."""
    image_name = "rhel-sap-v20220719"
    version = gcp.parse_image_version_from_name(image_name)

    assert version == "unknown"


def test_format_image():
    """Test transforming a single google image into a schmea approved
    format."""
    mocked_image = {
        "id": "rhel-7-v20220719",
        "architecture": "x86_64",
        "creation_timestamp": "2022-09-20T16:32:45.572-07:00",
        "description": "Red Hat, Red Hat Enterprise Linux, 7, x86_64",
        "name": "rhel-7-v20220920",
    }

    data = {"images": {"google": [gcp.format_image(mocked_image)]}}

    try:
        schema.validate_json(data)
    except ValidationError as exc:
        raise AssertionError(f"Formatted data does not expect schema: {exc}")


def test_format_all_images(mock_gcp_images):
    """Test transforming a list of google images into a schema approved
    format."""
    data = gcp.format_all_images()

    try:
        schema.validate_json(data)
    except ValidationError as exc:
        raise AssertionError(f"Formatted data does not expect schema: {exc}")
