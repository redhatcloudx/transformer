"""Test image updates from remote cloud APIs."""
from __future__ import annotations

from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

from src.rhelocator import update_images


def test_get_aws_regions() -> None:
    """Test AWS region request."""
    with patch("botocore.client.BaseClient._make_api_call") as boto:
        update_images.get_aws_regions()

    boto.assert_called_with("DescribeRegions", {"AllRegions": "True"})


def test_get_aws_hourly_images() -> None:
    """Test AWS image request."""
    with patch("botocore.client.BaseClient._make_api_call") as boto:
        update_images.get_aws_hourly_images("us-east-1")

    boto.assert_called_with(
        "DescribeImages", {"IncludeDeprecated": "False", "Owners": ["309956199498"]}
    )


@patch("src.rhelocator.update_images.get_aws_hourly_images")
@patch("src.rhelocator.update_images.get_aws_regions")
def test_get_aws_all_hourly_images(
    mock_regions: MagicMock, mock_images: MagicMock
) -> None:
    """Test retrieving all AWS hourly images from all regions."""
    # Fake the regions and images values.
    mock_regions.return_value = ["region1", "region2", "region3"]
    mock_images.return_value = ["image1", "image2", "image3"]

    images = update_images.get_aws_all_hourly_images()

    assert isinstance(images, dict)
    print(images.keys())
    assert list(images.keys()) == ["region1", "region2", "region3"]
    assert images["region1"] == ["image1", "image2", "image3"]


@patch("rhelocator.update_images.requests.post")
def test_get_azure_access_token(mock_requests: MagicMock) -> None:
    """Test retrieving Azure locations."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"foo": "bar", "access_token": "secrete"}
    mock_requests.return_value = mock_response

    access_token = update_images.get_azure_access_token()
    assert access_token == "secrete"  # nosec B105


@patch("rhelocator.update_images.requests.get")
def test_get_azure_locations(mock_requests: MagicMock) -> None:
    """Test getting Azure location list."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "value": [
            {
                "id": "/subscriptions/id/locations/eastus",
                "name": "eastus",
                "displayName": "East US",
                "regionalDisplayName": "(US) East US",
                "metadata": {
                    "regionType": "Physical",
                    "regionCategory": "Recommended",
                    "geographyGroup": "US",
                    "longitude": "-79.8164",
                    "latitude": "37.3719",
                    "physicalLocation": "Virginia",
                    "pairedRegion": [
                        {
                            "name": "westus",
                            "id": "/subscriptions/id/locations/westus",
                        }
                    ],
                },
            },
        ]
    }
    mock_requests.return_value = mock_response

    regions = update_images.get_azure_locations("secrete")
    assert regions == ["eastus"]


@patch("rhelocator.update_images.compute_v1.ImagesClient")
def test_get_google_images(mock_gcp: MagicMock) -> None:
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

    images = update_images.get_google_images()
    assert images == ["valid_image"]
