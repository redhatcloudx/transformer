"""Test image updates from remote cloud APIs."""
from __future__ import annotations

from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

from jsonschema import ValidationError

from rhelocator import config
from rhelocator.update_images import azure
from rhelocator.update_images import schema


@patch("rhelocator.update_images.azure.requests.post")
def test_get_access_token(mock_post) -> None:
    """Test retrieving Azure locations."""
    auth_response = {"foo": "bar", "access_token": "secrete"}
    mock_post.return_value = Mock(ok=True)
    mock_post.return_value.json.return_value = auth_response

    access_token = azure.get_access_token()

    assert access_token == "secrete"  # nosec B105


@patch("rhelocator.update_images.azure.requests.get")
def test_get_locations(mock_requests: MagicMock) -> None:
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
    with patch("rhelocator.update_images.azure.get_access_token") as mock_token:
        mock_token.return_value = "secrete"
        regions = azure.get_locations()

    assert regions == ["eastus"]


@patch("rhelocator.update_images.azure.requests.get")
def test_get_publishers(mock_get):
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

    publishers = azure.get_publishers("eastus")
    assert publishers == [publisher_response[0]["name"]]


@patch("rhelocator.update_images.azure.requests.get")
def test_get_offers(mock_get):
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

    offers = azure.get_offers("eastus", "publisher")
    assert offers == [offer_response[0]["name"]]


@patch("rhelocator.update_images.azure.requests.get")
def test_get_skus(mock_get):
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

    skus = azure.get_skus("eastus", "publisher", "offer")
    assert skus == [sku_response[0]["name"]]


@patch("rhelocator.update_images.azure.requests.get")
def test_get_image_versions(mock_get):
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
    image_versions = azure.get_image_versions("eastus", "publisher", "offer", "sku")
    assert image_versions == [image_versions_response[-1]["name"]]

    # Now try to get all of the images.
    image_versions = azure.get_image_versions(
        "eastus", "publisher", "offer", "sku", latest=False
    )
    assert image_versions == [x["name"] for x in image_versions_response]


@patch("rhelocator.update_images.azure.requests.get")
def test_get_image_details(mock_get):
    """Test retrieving Azure image details."""
    image_details_response = {
        "id": "a very long ID",
        "location": "westus",
        "name": "7.9.2022032206",
        "properties": {
            "architecture": "x64",
            "automaticOSUpgradeProperties": {"automaticOSUpgradeSupported": False},
            "dataDiskImages": [],
            "disallowed": {"vmDiskType": "Unmanaged"},
            "features": [{"name": "IsAcceleratedNetworkSupported", "value": "True"}],
            "hyperVGeneration": "V2",
            "imageDeprecationStatus": {"imageState": "Active"},
            "osDiskImage": {"operatingSystem": "Linux", "sizeInGb": 64},
            "replicaCount": 10,
            "replicaType": "Managed",
        },
    }

    mock_get.return_value = Mock(ok=True)
    mock_get.return_value.json.return_value = image_details_response

    image_details = azure.get_image_details(
        "eastus", "publisher", "offer", "sku", "version"
    )
    assert (
        image_details["properties"]["architecture"]
        == image_details_response["properties"]["architecture"]
    )
    assert (
        image_details["properties"]["hyperVGeneration"]
        == image_details_response["properties"]["hyperVGeneration"]
    )


def test_get_latest_images(mock_azure_image_versions_latest, mock_azure_image_details):
    """Test retrieving Azure images."""
    images = azure.get_images()

    assert isinstance(images, list)

    # Make sure we have the right keys that match Azure's specification.
    assert sorted(images[0].keys()) == [
        "architecture",
        "hyperVGeneration",
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


def test_get_all_images(mock_azure_image_versions, mock_azure_image_details):
    """Test retrieving Azure images when we want all of the image versions."""
    # Fake an image tree with one SKU that doesn't use 'latest'.
    config.AZURE_RHEL_IMAGE_TREE = {"redhat": {"RHEL": {"7lvm-gen2": ""}}}
    images = azure.get_images()

    assert isinstance(images, list)

    # Since we're looking for all image versions instead of just the latest ones, we
    # should have multiple image versions returned.
    assert len(images) == len(mock_azure_image_versions.return_value)


def test_format_image():
    """Test transforming a single Azure image into a schema approved format."""
    mocked_image = {
        "architecture": "x86_64",
        "hyperVGeneration": "v2",
        "offer": "offer",
        "publisher": "publisher",
        "sku": "sku",
        "urn": "publisher:offer:sku:7.6.2020082423",
        "version": "7.6.2020082423",
    }

    data = {"images": {"azure": [azure.format_image(mocked_image)]}}

    try:
        schema.validate_json(data)
    except ValidationError as exc:
        raise AssertionError(f"Formatted data does not expect schema: {exc}")


def test_format_all_images(mock_azure_images):
    """Test transforming a list of Azure images into a schema approved
    format."""
    data = azure.format_all_images()

    try:
        schema.validate_json(data)
    except ValidationError as exc:
        raise AssertionError(f"Formatted data does not expect schema: {exc}")
