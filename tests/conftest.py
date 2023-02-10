"""Configuration for tests."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest


MOCKED_AWS_IMAGE_LIST = [
    {
        "ImageId": "ami-0001",
        "UsageOperation": "RunInstances:0010",
        "Architecture": "x86_64",
        "CreationDate": "2021-02-10T16:19:48.000Z",
        "Name": "RHEL-8.3_HVM-20210209-x86_64-0-Hourly2-GP2",
        "VirtualizationType": "hvm",
    },
    {
        "ImageId": "ami-0002",
        "UsageOperation": "RunInstances:0010",
        "Architecture": "x86_64",
        "CreationDate": "2021-02-10T16:19:48.000Z",
        "Name": "RHEL-8.3_HVM-20210209-x86_64-0-Hourly2-GP2",
        "VirtualizationType": "hvm",
    },
    {
        "ImageId": "ami-0003",
        "UsageOperation": "RunInstances:0000",
        "Architecture": "x86_64",
        "CreationDate": "2021-02-10T16:19:48.000Z",
        "Name": "RHEL-8.3_HVM-20210209-x86_64-0-Access2-GP2",
        "VirtualizationType": "hvm",
    },
]

MOCKED_AZURE_IMAGE_LIST = [
    {
        "architecture": "x86_64",
        "hyperVGeneration": "v2",
        "offer": "offer",
        "publisher": "publisher",
        "sku": "sku",
        "urn": "publisher:offer:sku:9.0.2022053014",
        "version": "9.0.2022053014",
    },
    {
        "architecture": "x86_64",
        "hyperVGeneration": "v2",
        "offer": "offer",
        "publisher": "publisher",
        "sku": "sku",
        "urn": "publisher:offer:sku:9.0.2022062014",
        "version": "9.0.2022062014",
    },
    {
        "architecture": "x86_64",
        "hyperVGeneration": "v2",
        "offer": "offer",
        "publisher": "publisher",
        "sku": "sku",
        "urn": "publisher:offer:sku:9.0.2022062414",
        "version": "9.0.2022062414",
    },
]

MOCKED_AZURE_IMAGE_VERSION_LIST = [
    "9.0.2022053014",
    "9.0.2022062014",
    "9.0.2022062414",
    "9.0.2022081801",
    "9.0.2022090601",
    "9.1.2022112101"
]

MOCKED_AZURE_IMAGE_VERSION = [
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/RHEL/Skus/9-lvm-gen2/Versions/9.0.2022053014",
    "location": "westus",
    "name": "9.0.2022053014"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/RHEL/Skus/9-lvm-gen2/Versions/9.0.2022062014",
    "location": "westus",
    "name": "9.0.2022062014"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/RHEL/Skus/9-lvm-gen2/Versions/9.0.2022062414",
    "location": "westus",
    "name": "9.0.2022062414"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/RHEL/Skus/9-lvm-gen2/Versions/9.0.2022081801",
    "location": "westus",
    "name": "9.0.2022081801"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/RHEL/Skus/9-lvm-gen2/Versions/9.0.2022090601",
    "location": "westus",
    "name": "9.0.2022090601"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/RHEL/Skus/9-lvm-gen2/Versions/9.1.2022112101",
    "location": "westus",
    "name": "9.1.2022112101"
  }
]

MOCKED_AZURE_IMAGE_DETAILS = {
  "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/RHEL/Skus/9-lvm-gen2/Versions/9.0.2022053014",
  "location": "westus",
  "name": "9.0.2022053014",
  "properties": {
    "architecture": "x64",
    "automaticOSUpgradeProperties": {
      "automaticOSUpgradeSupported": "false"
    },
    "dataDiskImages": [],
    "disallowed": {
      "vmDiskType": "Unmanaged"
    },
    "features": [
      {
        "name": "SecurityType",
        "value": "TrustedLaunchSupported"
      },
      {
        "name": "IsAcceleratedNetworkSupported",
        "value": "True"
      },
      {
        "name": "DiskControllerTypes",
        "value": "SCSI"
      },
      {
        "name": "IsHibernateSupported",
        "value": "False"
      }
    ],
    "hyperVGeneration": "V2",
    "imageDeprecationStatus": {
      "imageState": "Active"
    },
    "osDiskImage": {
      "operatingSystem": "Linux",
      "sizeInGb": 64
    },
    "replicaCount": 10,
    "replicaType": "Managed"
  }
}

MOCKED_AZURE_IMAGE_SKUS_LIST = [
    "6.10",
    "7-LVM",
    "7-RAW",
    "7-RAW-CI",
    "7.2",
    "7.3",
    "7.3-DAILY",
    "7.4",
    "7.5",
    "7.6",
    "7.7",
    "7.8",
    "74-gen2",
    "75-gen2",
    "76-gen2",
    "77-gen2",
    "78-gen2",
    "79-gen2",
    "7lvm-gen2",
    "7_9",
    "8",
    "8-BETA",
    "8-gen2",
    "8-LVM",
    "8-lvm-gen2",
    "8.1",
    "8.1-ci",
    "8.2",
    "81-ci-gen2",
    "81gen2",
    "82gen2",
    "83-gen2",
    "84-gen2",
    "85-gen2",
    "86-gen2",
    "87-gen2",
    "8_3",
    "8_4",
    "8_5",
    "8_6",
    "8_7",
    "9-lvm",
    "9-lvm-gen2",
    "90-gen2",
    "91-gen2",
    "9_0",
    "9_1"
]

MOCKED_AZURE_IMAGE_SKUS = [
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/RHEL/Skus/6.10",
    "location": "westus",
    "name": "6.10",
    "properties": {
      "automaticOSUpgradeProperties": {
        "automaticOSUpgradeSupported": "false"
      }
    }
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/RHEL/Skus/7-LVM",
    "location": "westus",
    "name": "7-LVM",
    "properties": {
      "automaticOSUpgradeProperties": {
        "automaticOSUpgradeSupported": "false"
      }
    }
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/RHEL/Skus/7-RAW",
    "location": "westus",
    "name": "7-RAW",
    "properties": {
      "automaticOSUpgradeProperties": {
        "automaticOSUpgradeSupported": "false"
      }
    }
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/RHEL/Skus/7-RAW-CI",
    "location": "westus",
    "name": "7-RAW-CI",
    "properties": {
      "automaticOSUpgradeProperties": {
        "automaticOSUpgradeSupported": "false"
      }
    }
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/RHEL/Skus/7.2",
    "location": "westus",
    "name": "7.2",
    "properties": {
      "automaticOSUpgradeProperties": {
        "automaticOSUpgradeSupported": "false"
      }
    }
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/RHEL/Skus/7.3",
    "location": "westus",
    "name": "7.3",
    "properties": {
      "automaticOSUpgradeProperties": {
        "automaticOSUpgradeSupported": "false"
      }
    }
  },
]

MOCKED_AZURE_OFFERS = [
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/alfredtestoffer",
    "location": "westus",
    "name": "alfredtestoffer"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/osa",
    "location": "westus",
    "name": "osa"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/rh-ocp-worker",
    "location": "westus",
    "name": "rh-ocp-worker"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/rh-oke-worker",
    "location": "westus",
    "name": "rh-oke-worker"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/rh-opp-worker",
    "location": "westus",
    "name": "rh-opp-worker"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/rh-rhel",
    "location": "westus",
    "name": "rh-rhel"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/RHEL",
    "location": "westus",
    "name": "RHEL"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/rhel-arm64",
    "location": "westus",
    "name": "rhel-arm64"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/rhel-byos",
    "location": "westus",
    "name": "rhel-byos"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/rhel-byos-test",
    "location": "westus",
    "name": "rhel-byos-test"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/rhel-cpp-test",
    "location": "westus",
    "name": "rhel-cpp-test"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/RHEL-HA",
    "location": "westus",
    "name": "RHEL-HA"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/rhel-raw",
    "location": "westus",
    "name": "rhel-raw"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/RHEL-SAP",
    "location": "westus",
    "name": "RHEL-SAP"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/RHEL-SAP-APPS",
    "location": "westus",
    "name": "RHEL-SAP-APPS"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/RHEL-SAP-HA",
    "location": "westus",
    "name": "RHEL-SAP-HA"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/rhel-sig-publishing-test",
    "location": "westus",
    "name": "rhel-sig-publishing-test"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/RHEL-TEST",
    "location": "westus",
    "name": "RHEL-TEST"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/rhel_test_offers",
    "location": "westus",
    "name": "rhel_test_offers"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/rh_rhel_7_latest",
    "location": "westus",
    "name": "rh_rhel_7_latest"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/rh_rhel_7_vm",
    "location": "westus",
    "name": "rh_rhel_7_vm"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/rh_rhel_8_latest",
    "location": "westus",
    "name": "rh_rhel_8_latest"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/rh_rhel_8_main_1",
    "location": "westus",
    "name": "rh_rhel_8_main_1"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/rh_rhel_8_vm",
    "location": "westus",
    "name": "rh_rhel_8_vm"
  },
  {
    "id": "/Subscriptions/a5192c85-2bff-4433-ac37-69aad5fcc86a/Providers/Microsoft.Compute/Locations/westus/Publishers/redhat/ArtifactTypes/VMImage/Offers/test_offer_china",
    "location": "westus",
    "name": "test_offer_china"
  }
]

MOCKED_AZURE_ACCESS_TOKEN = "access_token"


def pytest_configure(config) -> None:
    config.addinivalue_line("markers", "e2e: mark as end-to-end test.")


@pytest.fixture
def mock_aws_regions(mocker):
    """Provide an offline result for calls to get_aws_regions."""
    mock = mocker.patch("cloudimagedirectory.update_images.aws.get_regions")
    mock.return_value = ["us-east-1", "us-east-2"]
    return mock


@pytest.fixture
def mock_aws_images(mocker):
    """Provide an offline result for calls to get_aws_images."""
    mock = mocker.patch("cloudimagedirectory.update_images.aws.describe_images")
    mock.return_value = MOCKED_AWS_IMAGE_LIST
    return mock


@pytest.fixture
def mock_azure_access_token(mocker):
    """Provide an offline result got get_azure_image_versions."""
    mock = mocker.patch("cloudimagedirectory.update_images.azure.get_access_token")
    mock.return_value = MOCKED_AZURE_ACCESS_TOKEN
    return mock

@pytest.fixture
def mock_azure_image_skus(mocker):
    """Provide an offline result got get_azure_image_skus."""
    mock = mocker.patch("cloudimagedirectory.update_images.azure.get_request")
    mock.return_value = MOCKED_AZURE_IMAGE_SKUS
    return mock

@pytest.fixture
def mock_azure_image_skus_list(mocker):
    """Provide an offline result got get_azure_image_skus_list."""
    mock = mocker.patch("cloudimagedirectory.update_images.azure.get_skus")
    mock.return_value = MOCKED_AZURE_IMAGE_SKUS_LIST
    return mock

@pytest.fixture
def mock_azure_offers(mocker):
    """Provide an offline result got get_azure_offers."""
    mock = mocker.patch("cloudimagedirectory.update_images.azure.get_offers")
    mock.return_value = MOCKED_AZURE_OFFERS
    return mock

@pytest.fixture
def mock_azure_image_version(mocker):
    """Provide an offline result got get_azure_image_version."""
    mock = mocker.patch("cloudimagedirectory.update_images.azure.get_images.get_image_versions.get_request")
    mock.return_value = MOCKED_AZURE_IMAGE_VERSION
    return mock

@pytest.fixture
def mock_azure_image_version_list(mocker):
    """Provide an offline result got get_azure_image_versions."""
    mock = mocker.patch("cloudimagedirectory.update_images.azure.get_image_versions")
    mock.return_value = MOCKED_AZURE_IMAGE_VERSION_LIST
    return mock


@pytest.fixture
def mock_azure_image_versions_latest(mocker):
    """Provide an offline result got get_azure_image_versions."""
    mock = mocker.patch("cloudimagedirectory.update_images.azure.get_image_versions")
    mock.return_value = [MOCKED_AZURE_IMAGE_VERSION_LIST[0]]
    return mock


@pytest.fixture
def mock_azure_image_details(mocker):
    """Provide an offline result got get_azure_image_details."""
    mock = mocker.patch("cloudimagedirectory.update_images.azure.get_image_details")
    mock.return_value = MOCKED_AZURE_IMAGE_DETAILS
    return mock


@pytest.fixture
def mock_azure_images(mocker):
    """Provide an offline result for calls to azure.get_images."""
    mock = mocker.patch("cloudimagedirectory.update_images.azure.get_images")
    mock.return_value = MOCKED_AZURE_IMAGE_LIST
    return mock


@pytest.fixture
def mock_google_images(mocker):
    """Provide an offline result for calls to get_google_images."""
    mock = mocker.patch("cloudimagedirectory.update_images.google.get_images")

    mocked_image = {
        "id": "rhel-7-9-sap-v20220719",
        "architecture": "x86_64",
        "creation_timestamp": "2022-09-20T16:32:45.572-07:00",
        "description": "Red Hat, Red Hat Enterprise Linux, 7, x86_64",
        "name": "rhel-7-v20220920",
    }
    mock.return_value = [mocked_image]

    return mock


@pytest.fixture
def mock_normalize_google_images(mocker):
    """Provide an offline result for calls to normalize_google_images."""
    mock = mocker.patch(
        "cloudimagedirectory.update_images.google.normalize_google_images"
    )

    # Fake a Google image listing.
    mocked_image = MagicMock()
    mocked_image.architecture = "X86_64"
    mocked_image.creation_timestamp = "20221018"
    mocked_image.description = "RHEL"
    mocked_image.name = "rhel-9-20221018"
    mock.return_value = [mocked_image]

    return mock
