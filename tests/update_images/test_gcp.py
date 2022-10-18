"""Test image updates from remote cloud APIs."""
from __future__ import annotations

from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

from rhelocator.update_images import gcp


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
