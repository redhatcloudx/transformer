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
        "DescribeImages",
        {"IncludeDeprecated": False, "Owners": [config.AWS_RHEL_OWNER_ID]},
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


def test_parse_aws_image_name_basic():
    """Test parsing an AWS image name with a very basic image."""
    image_name = "RHEL-7.9_HVM-20220512-x86_64-1-Hourly2-GP2"
    data = update_images.parse_aws_image_name(image_name)

    assert isinstance(data, dict)

    assert not data["intprod"]
    assert not data["extprod"]
    assert data["version"] == "7.9"
    assert data["virt"] == "HVM"
    assert not data["beta"]
    assert data["date"] == "20220512"
    assert data["arch"] == "x86_64"
    assert data["release"] == "1"
    assert data["billing"] == "Hourly2"
    assert data["storage"] == "GP2"


def test_parse_aws_image_name_beta():
    """Test parsing an AWS image name for a beta arm64 image."""
    image_name = "RHEL-9.1.0_HVM_BETA-20220829-arm64-0-Hourly2-GP2"
    data = update_images.parse_aws_image_name(image_name)

    assert isinstance(data, dict)

    assert not data["intprod"]
    assert not data["extprod"]
    assert data["version"] == "9.1.0"
    assert data["virt"] == "HVM"
    assert data["beta"] == "BETA"
    assert data["date"] == "20220829"
    assert data["arch"] == "arm64"
    assert data["release"] == "0"
    assert data["billing"] == "Hourly2"
    assert data["storage"] == "GP2"


def test_parse_aws_image_name_internal_product():
    """Test parsing an AWS image name with an internal product."""
    image_name = "RHEL_HA-8.5.0_HVM-20211103-x86_64-0-Hourly2-GP2"
    data = update_images.parse_aws_image_name(image_name)

    assert isinstance(data, dict)

    assert data["intprod"] == "HA"
    assert not data["extprod"]
    assert data["version"] == "8.5.0"
    assert data["virt"] == "HVM"
    assert not data["beta"]
    assert data["date"] == "20211103"
    assert data["arch"] == "x86_64"
    assert data["release"] == "0"
    assert data["billing"] == "Hourly2"
    assert data["storage"] == "GP2"


def test_parse_aws_image_name_external_product():
    """Test parsing an AWS image name for a beta arm64 image."""
    image_name = "RHEL-SAP-8.2.0_HVM-20211007-x86_64-0-Hourly2-GP2"
    data = update_images.parse_aws_image_name(image_name)

    assert isinstance(data, dict)

    assert not data["intprod"]
    assert data["extprod"] == "SAP"
    assert data["version"] == "8.2.0"
    assert data["virt"] == "HVM"
    assert not data["beta"]
    assert data["date"] == "20211007"
    assert data["arch"] == "x86_64"
    assert data["release"] == "0"
    assert data["billing"] == "Hourly2"
    assert data["storage"] == "GP2"


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


@patch("rhelocator.update_images.requests.get")
def test_get_azure_publishers(mock_get):
    """Test retrieving and filtering Azure publishers."""
    publisher_response = [
        {
            "name": "aaaaaaaa",
            "location": "aaaaaaaaaaaaaaaaaa",
            "tags": {"key7868": "aaaaa"},
            "extendedLocation": {"name": "aaaaaaaaaaaaaaaaaaaaa", "type": "EdgeZone"},
            "id": "aaaaaaaaaaa",
        }
    ]
    mock_get.return_value = Mock(ok=True)
    mock_get.return_value.json.return_value = publisher_response

    publishers = update_images.get_azure_publishers("eastus")
    assert publishers == [publisher_response[0]["name"]]


@patch("rhelocator.update_images.requests.get")
def test_get_azure_offers(mock_get):
    """Test retrieving and filtering Azure offers."""
    offer_response = [
        {
            "name": "aaaaaaaa",
            "location": "aaaaaaaaaaaaaaaaaa",
            "tags": {"key7868": "aaaaa"},
            "extendedLocation": {"name": "aaaaaaaaaaaaaaaaaaaaa", "type": "EdgeZone"},
            "id": "aaaaaaaaaaa",
        }
    ]
    mock_get.return_value = Mock(ok=True)
    mock_get.return_value.json.return_value = offer_response

    offers = update_images.get_azure_offers("eastus", "publisher")
    assert offers == [offer_response[0]["name"]]


@patch("rhelocator.update_images.requests.get")
def test_get_azure_skus(mock_get):
    """Test retrieving and filtering Azure SKUs."""
    sku_response = [
        {
            "name": "aaaaaaaa",
            "location": "aaaaaaaaaaaaaaaaaa",
            "tags": {"key7868": "aaaaa"},
            "extendedLocation": {"name": "aaaaaaaaaaaaaaaaaaaaa", "type": "EdgeZone"},
            "id": "aaaaaaaaaaa",
        }
    ]
    mock_get.return_value = Mock(ok=True)
    mock_get.return_value.json.return_value = sku_response

    skus = update_images.get_azure_skus("eastus", "publisher", "offer")
    assert skus == [sku_response[0]["name"]]


@patch("rhelocator.update_images.requests.get")
def test_get_azure_image_versions(mock_get):
    """Test retrieving and filtering Azure image versions."""
    image_versions_response = [
        {
            "location": "eastus",
            "name": "9.0.2022053014",
            "id": "9-lvm-gen2/Versions/9.0.2022053014",
        },
        {
            "location": "eastus",
            "name": "9.0.2022062014",
            "id": "9-lvm-gen2/Versions/9.0.2022062014",
        },
        {
            "location": "eastus",
            "name": "9.0.2022062414",
            "id": "9-lvm-gen2/Versions/9.0.2022062414",
        },
        {
            "location": "eastus",
            "name": "9.0.2022081801",
            "id": "9-lvm-gen2/Versions/9.0.2022081801",
        },
        {
            "location": "eastus",
            "name": "9.0.2022090601",
            "id": "9-lvm-gen2/Versions/9.0.2022090601",
        },
    ]
    mock_get.return_value = Mock(ok=True)
    mock_get.return_value.json.return_value = image_versions_response

    # Try with the default where we only get the latest image.
    image_versions = update_images.get_azure_image_versions(
        "eastus", "publisher", "offer", "sku"
    )
    assert image_versions == [image_versions_response[-1]["name"]]

    # Now try to get all of the images.
    image_versions = update_images.get_azure_image_versions(
        "eastus", "publisher", "offer", "sku", latest=False
    )
    assert image_versions == [x["name"] for x in image_versions_response]


def test_get_latest_azure_images(mock_azure_image_versions_latest):
    """Test retrieving Azure images."""
    images = update_images.get_azure_images()

    assert isinstance(images, list)

    # Make sure we have the right keys that match Azure's specification.
    assert sorted(images[0].keys()) == [
        "offer",
        "publisher",
        "sku",
        "urn",
        "version",
    ]

    # Loop through each image to ensure the URN is set properly.
    for image in images:
        urn_sections = [
            image["publisher"],
            image["offer"],
            image["sku"],
            image["version"],
        ]
        assert image["urn"] == ":".join(urn_sections)

    # Since we asked for the latest image only, we should have one image per SKU.
    assert len({x["sku"] for x in images}) == len(images)


def test_get_all_azure_images(mock_azure_image_versions):
    """Test retrieving Azure images when we want all of the image versions."""
    # Fake an image tree with one SKU that doesn't use 'latest'.
    config.AZURE_RHEL_IMAGE_TREE = {"redhat": {"RHEL": {"7lvm-gen2": ""}}}
    images = update_images.get_azure_images()

    assert isinstance(images, list)

    # Since we're looking for all image versions instead of just the latest ones, we
    # should have multiple image versions returned.
    assert len(images) == len(mock_azure_image_versions.return_value)


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
