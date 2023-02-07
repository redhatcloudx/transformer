"""Test image updates from remote cloud APIs."""
from __future__ import annotations

import json

from unittest.mock import MagicMock
from unittest.mock import patch

from jsonschema import ValidationError

from cloudimagedirectory.update_images import google
from cloudimagedirectory.update_images import schema


@patch("cloudimagedirectory.update_images.google.compute_v1.ImagesClient")
def test_get_images(mock_google: MagicMock) -> None:
    """Test getting Google images."""
    fam_rhel_images = []
    with open("tests/update_images/testdata/google_list_images.json") as json_file:
        list = json.load(json_file)
        for entry in list:
            if entry["family"].__contains__("rhel"):
                fam_rhel_images.append(entry)

    mocked_list = []

    for image in fam_rhel_images:
        # Fake a deprecated Google image listing.
        mocked_deprecated_image = MagicMock()
        mocked_deprecated_image.architecture = image["architecture"]
        mocked_deprecated_image.creation_timestamp = image["creationTimestamp"]
        mocked_deprecated_image.description = image["description"]
        mocked_deprecated_image.name = "DEPRECATED"
        mocked_deprecated_image.deprecated.state = "DEPRECATED"

        mocked_list.append(mocked_deprecated_image)

        # Fake a valid Google image listing.
        mocked_valid_image = MagicMock()
        mocked_valid_image.architecture = image["architecture"]
        mocked_valid_image.creation_timestamp = image["creationTimestamp"]
        mocked_valid_image.description = image["description"]
        mocked_valid_image.name = image["name"]
        mocked_valid_image.deprecated.state = "READY"

        mocked_list.append(mocked_valid_image)

    # Connect the mock to the ImagesClient return value.
    mock_response = MagicMock()
    mock_response.list.return_value = mocked_list
    mock_google.return_value = mock_response

    images = google.get_images()

    deprecated_images = [image for image in images if image["name"] == "DEPRECATED"]
    assert len(deprecated_images) == 0


def test_normalize_google_images() -> None:
    """Test normalizing Google image data."""
    # Fake a Google image listing.
    mocked_image = MagicMock()
    mocked_image.architecture = "X86_64"
    mocked_image.creation_timestamp = "20221018"
    mocked_image.description = "RHEL"
    mocked_image.name = "rhel-9-20221018"

    images = google.normalize_google_images([mocked_image])

    assert isinstance(images, list)
    assert images[0] == {
        "architecture": "x86_64",
        "creation_timestamp": "20221018",
        "description": "RHEL",
        "name": "rhel-9-20221018",
    }


def test_parse_valid_image_name():
    """Test parsing a google image name with a basic image."""
    image_name = "rhel-7-9-sap-v20220719"
    data = google.parse_image_name(image_name)

    assert data["product"] == "rhel"
    assert data["extprod"] == "sap"
    assert data["version"] == "7-9"
    assert data["date"] == "20220719"


def test_parse_invalid_image_name():
    """Test parsing an invalid google image name."""
    image_name = "notarealname"
    data = google.parse_image_name(image_name)
    assert not data


def test_format_image():
    """Test transforming a single google image into a schema approved
    format."""
    mocked_image = {
        "id": "rhel-7-v20220719",
        "architecture": "x86_64",
        "creation_timestamp": "2022-09-20T16:32:45.572-07:00",
        "description": "Red Hat, Red Hat Enterprise Linux, 7, x86_64",
        "name": "rhel-7-v20220920",
    }

    data = {"images": {"google": [google.format_image(mocked_image)]}}

    try:
        schema.validate_json(data)
    except ValidationError as exc:
        raise AssertionError(f"Formatted data does not expect schema: {exc}")


def test_format_image_with_arch_in_name():
    """Test transforming a single google image into a schema approved format if
    name contains architecture instead of external product."""
    mocked_image = {
        "id": "3359998819149417250",
        "architecture": "ARM64",
        "creation_timestamp": "2022-09-20T16:32:45.572-07:00",
        "description": "Red Hat, Red Hat Enterprise Linux, 9",
        "name": "rhel-9-arm64-v20221206",
    }

    formatted = google.format_image(mocked_image)
    data = {"images": {"google": [formatted]}}

    assert formatted["name"] == "RHEL 9 arm64"

    try:
        schema.validate_json(data)
    except ValidationError as exc:
        raise AssertionError(f"Formatted data does not expect schema: {exc}")


def test_format_all_images(mock_google_images):
    """Test transforming a list of google images into a schema approved
    format."""
    data = google.format_all_images()

    try:
        schema.validate_json(data)
    except ValidationError as exc:
        raise AssertionError(f"Formatted data does not expect schema: {exc}")
