"""Test image updates from remote cloud APIs."""
from __future__ import annotations

from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from rhelocator import config
from rhelocator import update_images


def test_get_aws_regions() -> None:
    """Test AWS region request."""
    with patch("botocore.client.BaseClient._make_api_call") as boto:
        update_images.get_aws_regions()

    boto.assert_called_with("DescribeRegions", {"AllRegions": True})


def test_aws_describe_images() -> None:
    """Test AWS image request."""
    with patch("botocore.client.BaseClient._make_api_call") as boto:
        update_images.aws_describe_images("us-east-1")

    boto.assert_called_with(
        "DescribeImages", {"IncludeDeprecated": False, "Owners": ["309956199498"]}
    )


def test_get_aws_hourly_images(mock_aws_regions, mock_aws_images):
    """Ensure we filter for hourly images properly."""
    images = update_images.get_aws_images(region="us-east-1", image_type="hourly")

    billing_codes = {x["UsageOperation"] for x in images}
    assert billing_codes == {config.AWS_HOURLY_BILLING_CODE}


def test_get_aws_cloud_access_images(mock_aws_regions, mock_aws_images):
    """Ensure we filter for cloud access images properly."""
    images = update_images.get_aws_images(region="us-east-1", image_type="cloudaccess")

    billing_codes = {x["UsageOperation"] for x in images}
    assert billing_codes == {config.AWS_CLOUD_ACCESS_BILLING_CODE}


def test_get_aws_images_bogus_type(mock_aws_regions, mock_aws_images):
    """Test the exception if someone provides a bogus image type."""
    with pytest.raises(NotImplementedError):
        update_images.get_aws_images(region="us-east-1", image_type="doot")


def test_get_aws_all_images(mock_aws_regions, mock_aws_images) -> None:
    """Test retrieving all AWS hourly images from all regions."""
    images = update_images.get_aws_all_images()

    # Regions should be in the keys.
    assert list(images.keys()) == mock_aws_regions.return_value

    # Each region should have only hourly image billing codes.
    for _region, image_list in images.items():
        billing_codes = {x["UsageOperation"] for x in image_list}
        assert billing_codes == {config.AWS_HOURLY_BILLING_CODE}


@patch("rhelocator.update_images.requests.post")
def test_get_azure_access_token(mock_post) -> None:
    """Test retrieving Azure locations."""
    auth_response = {"foo": "bar", "access_token": "secrete"}
    mock_post.return_value = Mock(ok=True)
    mock_post.return_value.json.return_value = auth_response

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

    # Fake the access token.
    with patch("rhelocator.update_images.get_azure_access_token") as mock_token:
        mock_token.return_value = "secrete"
        regions = update_images.get_azure_locations()

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
