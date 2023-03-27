"""Test image updates from remote cloud APIs."""
from __future__ import annotations

import json

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from jsonschema import ValidationError
from requests import RequestException

from cloudimagedirectory import config
from cloudimagedirectory.update_images import azure
from cloudimagedirectory.update_images import schema


@patch("cloudimagedirectory.update_images.azure.requests.post")
def test_get_access_token(mock_post: MagicMock) -> None:
    """Test retrieving Azure locations."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"foo": "bar", "access_token": "secret"}
    mock_post.return_value = mock_response

    access_token = azure.get_access_token()

    assert access_token == "secret"  # nosec B105


@patch("cloudimagedirectory.update_images.azure.requests.post")
def test_fail_to_get_access_token(mock_post: MagicMock) -> None:
    """Test retrieving Azure locations."""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"foo": "bar", "access_token": ""}
    mock_post.return_value = mock_response

    with pytest.raises(Exception, match=r"Unable to authenticate"):
        azure.get_access_token()


@patch(
    "cloudimagedirectory.update_images.azure.requests.post",
    side_effect=RequestException("Failed Request"),
)
def test_post_request_ambigious_request_error(mock_post: MagicMock) -> None:
    """Test executing safeguarded post request."""

    with pytest.raises(SystemExit):
        azure.get_access_token()


@patch(
    "cloudimagedirectory.update_images.azure.requests.get",
    side_effect=RequestException("Failed Request"),
)
def test_get_request_ambigious_request_error(mock_get: MagicMock) -> None:
    """Test executing safeguarded get request."""

    with pytest.raises(SystemExit):
        azure.get_request("https://foo.bar", {"foo": "bar"}, {"foo": "bar"})


@patch("cloudimagedirectory.update_images.azure.requests.get")
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
    with patch(
        "cloudimagedirectory.update_images.azure.get_access_token"
    ) as mock_token:
        mock_token.return_value = "secrete"
        regions = azure.get_locations("dummy_access_token")

    assert regions == ["eastus"]


@patch("cloudimagedirectory.update_images.azure.requests.get")
def test_fail_get_locations(mock_requests: MagicMock) -> None:
    """Test failing to get Azure location list."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_requests.return_value = mock_response

    with pytest.raises(Exception, match=r"Unable to retrieve locations."):
        azure.get_locations("dummy_access_token")


@patch("cloudimagedirectory.update_images.azure.requests.get")
def test_get_publishers(mock_get: MagicMock):
    """Test retrieving and filtering Azure publishers."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "name": "aaaaaaaa",
            "location": "aaaaaaaaaaaaaaaaaa",
            "tags": {"key7868": "aaaaa"},
            "extendedLocation": {"name": "aaaaaaaaaaaaaaaaaaaaa", "type": "EdgeZone"},
            "id": "aaaaaaaaaaa",
        }
    ]
    mock_get.return_value = mock_response

    publishers = azure.get_publishers("dummy_access_token", "eastus")
    assert publishers == [mock_response.json.return_value[0]["name"]]


@patch("cloudimagedirectory.update_images.azure.requests.get")
def test_fail_get_publishers(mock_requests: MagicMock) -> None:
    """Test failing to get Azure publisher list."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_requests.return_value = mock_response

    with pytest.raises(Exception, match=r"Unable to retrieve publishers."):
        azure.get_publishers("dummy_access_token", "dummy_location")


@patch("cloudimagedirectory.update_images.azure.requests.get")
def test_get_offers(mock_get: MagicMock):
    """Test retrieving and filtering Azure offers."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "name": "aaaaaaaa",
            "location": "aaaaaaaaaaaaaaaaaa",
            "tags": {"key7868": "aaaaa"},
            "extendedLocation": {"name": "aaaaaaaaaaaaaaaaaaaaa", "type": "EdgeZone"},
            "id": "aaaaaaaaaaa",
        }
    ]
    mock_get.return_value = mock_response

    offers = azure.get_offers("dummy_access_token", "eastus", "publisher")
    assert offers == [mock_response.json.return_value[0]["name"]]


@patch("cloudimagedirectory.update_images.azure.requests.get")
def test_fail_get_offers(mock_requests: MagicMock) -> None:
    """Test failing to get Azure offer list."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_requests.return_value = mock_response

    with pytest.raises(Exception, match=r"Unable to retrieve offers."):
        azure.get_offers("dummy_access_token", "dummy_location", "dummy_publisher")


@patch("cloudimagedirectory.update_images.azure.requests.get")
def test_get_skus(mock_get: MagicMock):
    """Test retrieving and filtering Azure SKUs."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "name": "aaaaaaaa",
            "location": "aaaaaaaaaaaaaaaaaa",
            "tags": {"key7868": "aaaaa"},
            "extendedLocation": {"name": "aaaaaaaaaaaaaaaaaaaaa", "type": "EdgeZone"},
            "id": "aaaaaaaaaaa",
        }
    ]
    mock_get.return_value = mock_response

    skus = azure.get_skus("dummy_access_token", "eastus", "publisher", "offer")
    assert skus == [mock_response.json.return_value[0]["name"]]


@patch("cloudimagedirectory.update_images.azure.requests.get")
def test_fail_get_skus(mock_requests: MagicMock) -> None:
    """Test failing to get Azure sku list."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_requests.return_value = mock_response

    with pytest.raises(Exception, match=r"Unable to retrieve skus."):
        azure.get_skus(
            "dummy_access_token", "dummy_location", "dummy_publisher", "dummy_offer"
        )


@patch("cloudimagedirectory.update_images.azure.requests.get")
def test_get_image_versions(mock_get: MagicMock):
    """Test retrieving and filtering Azure image versions."""

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
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
    mock_get.return_value = mock_response

    # Try with the default where we only get the latest image.
    image_versions = azure.get_image_versions(
        "dummy_access_token", "eastus", "publisher", "offer", "sku"
    )
    assert image_versions == [mock_response.json.return_value[-1]["name"]]

    # Now try to get all of the images.
    image_versions = azure.get_image_versions(
        "dummy_access_token", "eastus", "publisher", "offer", "sku", latest=False
    )
    assert image_versions == [x["name"] for x in mock_response.json.return_value]


@patch("cloudimagedirectory.update_images.azure.requests.get")
def test_fail_get_image_versions(mock_requests: MagicMock) -> None:
    """Test failing to get image versions."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_requests.return_value = mock_response

    with pytest.raises(Exception, match=r"Unable to retrieve image versions."):
        azure.get_image_versions(
            "dummy_access_token",
            "dummy_location",
            "dummy_publisher",
            "dummy_offer",
            "dummy_sku",
        )


@patch("cloudimagedirectory.update_images.azure.requests.get")
def test_get_image_details(mock_get: MagicMock):
    """Test retrieving Azure image details."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
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

    mock_get.return_value = mock_response

    image_details = azure.get_image_details(
        "dummy_access_token", "eastus", "publisher", "offer", "sku", "version"
    )
    assert (
        image_details["properties"]["architecture"]
        == mock_response.json.return_value["properties"]["architecture"]
    )
    assert (
        image_details["properties"]["hyperVGeneration"]
        == mock_response.json.return_value["properties"]["hyperVGeneration"]
    )


@patch("cloudimagedirectory.update_images.azure.requests.get")
def test_fail_get_image_details(mock_requests: MagicMock) -> None:
    """Test failing to get image details."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_requests.return_value = mock_response

    with pytest.raises(Exception, match=r"Unable to retrieve image details."):
        azure.get_image_details(
            "dummy_access_token",
            "dummy_location",
            "dummy_publisher",
            "dummy_offer",
            "dummy_sku",
            "dummy_version",
        )


def test_get_latest_images(
    mock_azure_access_token, mock_azure_image_version_list, mock_azure_image_details
):
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


def test_get_unique_skus(mock_azure_image_skus_list, mock_azure_access_token):
    """Test that the SKUs within each offer are unique."""
    for entry in config.AZURE_RHEL_IMAGE_TREE:
        for publisher, offers in entry.items():
            for offer in offers:
                skus = azure.get_skus(
                    azure.get_access_token(),
                    config.AZURE_DEFAULT_LOCATION,
                    publisher,
                    offer,
                )
                assert len(set(skus)) == len(skus)


def test_get_all_images(
    mock_azure_access_token, mock_azure_image_version_list, mock_azure_image_details
):
    """Test retrieving Azure images when we want all of the image versions."""
    # Fake an image tree with one SKU that doesn't use 'latest'.
    config.AZURE_RHEL_IMAGE_TREE = [{"redhat": {"RHEL": {"9-lvm-gen2": ""}}}]
    images = azure.get_images()

    assert isinstance(images, list)

    # Since we're looking for all image versions instead of just the latest ones, we
    # should have multiple image versions returned.
    assert len(images) == len(mock_azure_image_version_list.return_value)


def test_format_image():
    """Test verifying transformed Azure images into a schema approved
    format."""
    images = []
    with open("tests/update_images/testdata/azure_list_images.json") as json_file:
        images = json.load(json_file)

    for image in images:
        image["hyperVGeneration"] = "untested"
        image["version"] += ".2022053014"  # untested
        data = {"images": {"azure": [azure.format_image(image)]}}
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


def test_failing_to_parse_image_version():
    """Test expected failure behavior on supplying the parse function with an
    invalid image version."""
    invalid_version = "thisisnotaproperazureversion"

    parsed = azure.parse_image_version(invalid_version)

    assert parsed == {}


def test_convert_date():
    """Test successfully convert timestamp to date string."""
    yyyymmdd_date = azure.convert_date("20230124")

    assert yyyymmdd_date == "2023-01-24"

    yyyyddmm_date = azure.convert_date("20232401")

    assert yyyyddmm_date == "2023-01-24"


def test_fail_to_convert_date():
    """Test fail to convert broken timestamp."""
    with pytest.raises(Exception, match=r"unconverted data remains: 01"):
        azure.convert_date("20239901")

    with pytest.raises(Exception, match=r"unconverted data remains: 9"):
        azure.convert_date("20230199")
