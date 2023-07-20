"""Test Google image formatting."""
import re

import pytest
from cloudimagedirectory.format import format_google

# Download the latest Google data and then run:
# jq '.[] | select(.name | contains("rhel")) | .name' global.json
GOOGLE_NAMES = [
    "rhel-7-v20230711",
    "rhel-8-v20230711",
    "rhel-9-arm64-v20230713",
    "rhel-9-v20230711",
    "rhel-7-7-sap-v20230711",
    "rhel-7-9-sap-v20230711",
    "rhel-8-1-sap-v20230711",
    "rhel-8-2-sap-v20230711",
    "rhel-8-4-sap-v20230711",
    "rhel-8-6-sap-v20230711",
    "rhel-8-8-sap-v20230711",
    "rhel-9-0-sap-v20230711",
    "rhel-9-2-sap-v20230711",
]

GOOGLE_IMAGE_RECORD = {
    "architecture": "X86_64",
    "archiveSizeBytes": "7762438848",
    "creationTimestamp": "2023-07-11T16:20:27.045-07:00",
    "creation_timestamp": "2023-07-11T16:20:27.045-07:00",
    "description": (
        "Red Hat, Red Hat Enterprise Linux for SAP with HA and Update Services, 9.2, x86_64 built on 20230711"
    ),
    "diskSizeGb": "20",
    "family": "rhel-9-2-sap-ha",
    "guestOsFeatures": [
        {"type": "UEFI_COMPATIBLE"},
        {"type": "VIRTIO_SCSI_MULTIQUEUE"},
        {"type": "SEV_CAPABLE"},
        {"type": "GVNIC"},
    ],
    "id": "8802415689634700629",
    "kind": "compute#image",
    "labelFingerprint": "42WmSpB8rSM=",
    "licenseCodes": ["8291906032809750558"],
    "licenses": ["https://www.googleapis.com/compute/v1/projects/rhel-sap-cloud/global/licenses/rhel-9-sap"],
    "name": "rhel-9-2-sap-v20230711",
    "rawDisk": {"containerType": "TAR", "source": ""},
    "selfLink": "https://www.googleapis.com/compute/v1/projects/rhel-sap-cloud/global/images/rhel-9-2-sap-v20230711",
    "sourceType": "RAW",
    "status": "READY",
    "storageLocations": ["eu", "us", "asia"],
}


@pytest.mark.parametrize("image_name", GOOGLE_NAMES)
def test_parse_image_name(image_name: str) -> None:
    """Test parsing a Google image name."""
    result = format_google.GoogleRHELParser(image_name)
    assert result.product == "rhel"
    assert re.match(r"\d(\.\d)*", result.version)
    assert result.extprod in ["", "sap"]


def test_google_extract_project_name() -> None:
    """Test extracting a project name from the API selflink."""
    selflink = "https://www.googleapis.com/compute/v1/projects/rhel-sap-cloud/global/images/rhel-9-2-sap-v20230711"
    result = format_google.google_extract_project_name(selflink)
    assert result == "rhel-sap-cloud"


def test_google_extract_project_name_failure() -> None:
    """Test failing to extract a project name from a bad API selflink."""
    # Try with one that is too short.
    selflink = "i-like-dogs"
    with pytest.raises(format_google.InvalidSelfLink):
        assert format_google.google_extract_project_name(selflink)

    # Try with one that doesn't have projects in the right place.
    selflink = "/projects/can/be/challenging/to/manage/once/they/get/really/long/slash/slash"
    with pytest.raises(format_google.InvalidSelfLink):
        assert format_google.google_extract_project_name(selflink)


def test_google_selflink() -> None:
    """Test creating a selflink from a Google API selflink."""
    selflink = "https://www.googleapis.com/compute/v1/projects/rhel-sap-cloud/global/images/rhel-9-2-sap-v20230711"
    result = format_google.google_selflink(selflink)
    assert (
        result
        == "https://console.cloud.google.com/compute/imagesDetail/projects/rhel-sap-cloud/global/images/rhel-9-2-sap-v20230711"
    )


def test_image_rhel() -> None:
    """Test a full parse of an image."""
    result = format_google.image_rhel(GOOGLE_IMAGE_RECORD)
    assert result["name"] == "RHEL 9.2 sap X86_64"
    assert result["arch"] in ["X86_64", "arm64"]
    assert re.match(r"\d(\.\d)*", result["version"])
    assert result["imageId"] == GOOGLE_IMAGE_RECORD["selfLink"]
    assert result["date"] == GOOGLE_IMAGE_RECORD["creation_timestamp"]
    assert (
        result["selflink"]
        == "https://console.cloud.google.com/compute/imagesDetail/projects/rhel-sap-cloud/global/images/rhel-9-2-sap-v20230711"
    )
