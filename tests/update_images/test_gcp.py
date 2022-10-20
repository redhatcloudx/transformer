"""Test image updates from remote cloud APIs."""
from __future__ import annotations

from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from rhelocator import config
from rhelocator.update_images import gcp


@patch("rhelocator.update_images.gcp.compute_v1.ImagesClient")
def test_get_images(mock_gcp: MagicMock) -> None:
    """Test getting Google images."""
    # Fake a valid, non-deprecated image.
    mock_image = Mock()
    mock_image.name = "valid_image"

    # Fake a deprecated image.
    mock_deprecated_image = Mock()
    mock_deprecated_image.name = "deprecated_image"
    mock_deprecated_image.deprecated.state = "DEPRECATED"

    # Connect the mock to the ImagesClient return value.
    mock_response = MagicMock()
    mock_response.list.return_value = [mock_image, mock_deprecated_image]
    mock_gcp.return_value = mock_response

    images = gcp.get_images()
    assert images == ["valid_image"]
