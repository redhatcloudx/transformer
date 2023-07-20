"""Test AWS image formatting."""
import re

import pytest
from cloudimagedirectory.format import format_aws

# List made by getting a dump of the latest JSON file from AWS and running:
# jq '.[] | select(.OwnerId=="309956199498") | .Name' us-east-1.json | sort | uniq
AWS_NAMES = [
    "RHEL-7.9_HVM-20211005-x86_64-0-Hourly2-GP2",
    "RHEL-7.9_HVM-20220222-x86_64-0-Hourly2-GP2",
    "RHEL-7.9_HVM-20220512-x86_64-1-Hourly2-GP2",
    "RHEL-7.9_HVM-20221027-x86_64-0-Hourly2-GP2",
    "RHEL-8.1.0_HVM-20210907-arm64-0-Hourly2-GP2",
    "RHEL-8.1.0_HVM-20210907-x86_64-0-Hourly2-GP2",
    "RHEL-8.2.0_HVM-20210907-arm64-0-Hourly2-GP2",
    "RHEL-8.2.0_HVM-20210907-x86_64-0-Hourly2-GP2",
    "RHEL-8.4.0_HVM-20210825-arm64-0-Hourly2-GP2",
    "RHEL-8.4.0_HVM-20210825-x86_64-0-Hourly2-GP2",
    "RHEL-8.4.0_HVM-20230125-arm64-35-Hourly2-GP2",
    "RHEL-8.4.0_HVM-20230125-x86_64-35-Hourly2-GP2",
    "RHEL-8.4.0_HVM-20230307-arm64-12-Hourly2-GP2",
    "RHEL-8.4.0_HVM-20230307-x86_64-12-Hourly2-GP2",
    "RHEL-8.4.0_HVM-20230419-arm64-41-Hourly2-GP2",
    "RHEL-8.4.0_HVM-20230419-x86_64-41-Hourly2-GP2",
    "RHEL-8.5.0_HVM-20211103-arm64-0-Hourly2-GP2",
    "RHEL-8.5.0_HVM-20211103-x86_64-0-Hourly2-GP2",
    "RHEL-8.5.0_HVM_BETA-20210902-arm64-5-Hourly2-GP2",
    "RHEL-8.5.0_HVM_BETA-20210902-x86_64-5-Hourly2-GP2",
    "RHEL-8.5_HVM-20220127-arm64-3-Hourly2-GP2",
    "RHEL-8.5_HVM-20220127-x86_64-3-Hourly2-GP2",
    "RHEL-8.6.0_HVM-20220503-arm64-2-Hourly2-GP2",
    "RHEL-8.6.0_HVM-20220503-x86_64-2-Hourly2-GP2",
    "RHEL-8.6.0_HVM-20230118-arm64-30-Hourly2-GP2",
    "RHEL-8.6.0_HVM-20230118-x86_64-30-Hourly2-GP2",
    "RHEL-8.6.0_HVM-20230301-arm64-0-Hourly2-GP2",
    "RHEL-8.6.0_HVM-20230301-x86_64-0-Hourly2-GP2",
    "RHEL-8.6.0_HVM-20230411-arm64-60-Hourly2-GP2",
    "RHEL-8.6.0_HVM-20230411-x86_64-60-Hourly2-GP2",
    "RHEL-8.6.0_HVM_BETA-20220302-arm64-5-Hourly2-GP2",
    "RHEL-8.6.0_HVM_BETA-20220302-x86_64-5-Hourly2-GP2",
    "RHEL-8.7.0_HVM-20221101-arm64-0-Hourly2-GP2",
    "RHEL-8.7.0_HVM-20221101-x86_64-0-Hourly2-GP2",
    "RHEL-8.7.0_HVM-20230215-arm64-13-Hourly2-GP2",
    "RHEL-8.7.0_HVM-20230215-x86_64-13-Hourly2-GP2",
    "RHEL-8.7.0_HVM-20230330-arm64-56-Hourly2-GP2",
    "RHEL-8.7.0_HVM-20230330-x86_64-56-Hourly2-GP2",
    "RHEL-8.7.0_HVM_BETA-20220830-arm64-0-Hourly2-GP2",
    "RHEL-8.7.0_HVM_BETA-20220830-x86_64-0-Hourly2-GP2",
    "RHEL-8.8.0_HVM-20230503-arm64-54-Hourly2-GP2",
    "RHEL-8.8.0_HVM-20230503-x86_64-54-Hourly2-GP2",
    "RHEL-8.8.0_HVM-20230623-arm64-3-Hourly2-GP2",
    "RHEL-8.8.0_HVM-20230623-x86_64-3-Hourly2-GP2",
    "RHEL-8.8.0_HVM_BETA-20230228-arm64-22-Hourly2-GP2",
    "RHEL-8.8.0_HVM_BETA-20230228-x86_64-22-Hourly2-GP2",
    "RHEL-9.0.0_HVM-20220513-arm64-0-Hourly2-GP2",
    "RHEL-9.0.0_HVM-20220513-x86_64-0-Hourly2-GP2",
    "RHEL-9.0.0_HVM-20221027-arm64-1-Hourly2-GP2",
    "RHEL-9.0.0_HVM-20221027-x86_64-1-Hourly2-GP2",
    "RHEL-9.0.0_HVM-20230127-arm64-24-Hourly2-GP2",
    "RHEL-9.0.0_HVM-20230127-x86_64-24-Hourly2-GP2",
    "RHEL-9.0.0_HVM-20230313-arm64-43-Hourly2-GP2",
    "RHEL-9.0.0_HVM-20230313-x86_64-43-Hourly2-GP2",
    "RHEL-9.0.0_HVM-20230418-arm64-6-Hourly2-GP2",
    "RHEL-9.0.0_HVM-20230418-x86_64-6-Hourly2-GP2",
    "RHEL-9.0.0_HVM-20230531-arm64-4-Hourly2-GP2",
    "RHEL-9.0.0_HVM-20230531-x86_64-4-Hourly2-GP2",
    "RHEL-9.0.0_HVM_BETA-20211026-arm64-10-Hourly2-GP2",
    "RHEL-9.0.0_HVM_BETA-20211026-x86_64-10-Hourly2-GP2",
    "RHEL-9.1.0_HVM-20221101-arm64-2-Hourly2-GP2",
    "RHEL-9.1.0_HVM-20221101-x86_64-2-Hourly2-GP2",
    "RHEL-9.1.0_HVM-20230222-arm64-39-Hourly2-GP2",
    "RHEL-9.1.0_HVM-20230222-x86_64-39-Hourly2-GP2",
    "RHEL-9.1.0_HVM-20230404-arm64-54-Hourly2-GP2",
    "RHEL-9.1.0_HVM-20230404-x86_64-54-Hourly2-GP2",
    "RHEL-9.1.0_HVM_BETA-20220829-arm64-0-Hourly2-GP2",
    "RHEL-9.1.0_HVM_BETA-20220829-x86_64-0-Hourly2-GP2",
    "RHEL-9.2.0_HVM-20230503-arm64-41-Hourly2-GP2",
    "RHEL-9.2.0_HVM-20230503-x86_64-41-Hourly2-GP2",
    "RHEL-9.2.0_HVM-20230615-arm64-3-Hourly2-GP2",
    "RHEL-9.2.0_HVM-20230615-x86_64-3-Hourly2-GP2",
    "RHEL-9.2.0_HVM_BETA-20230306-arm64-4-Hourly2-GP2",
    "RHEL-9.2.0_HVM_BETA-20230306-x86_64-4-Hourly2-GP2",
    "RHEL_HA-7.9_HVM-20221027-x86_64-0-Hourly2-GP2",
    "RHEL_HA-8.2.0_HVM-20230228-x86_64-27-Hourly2-GP2",
    "RHEL_HA-8.2.0_HVM-20230411-x86_64-38-Hourly2-GP2",
    "RHEL_HA-8.2.0_HVM-20230529-x86_64-0-Hourly2-GP2",
    "RHEL_HA-8.4.0_HVM-20230125-x86_64-35-Hourly2-GP2",
    "RHEL_HA-8.4.0_HVM-20230307-x86_64-12-Hourly2-GP2",
    "RHEL_HA-8.4.0_HVM-20230419-x86_64-41-Hourly2-GP2",
    "RHEL_HA-8.5.0_HVM-20211103-x86_64-0-Hourly2-GP2",
    "RHEL_HA-8.5.0_HVM_BETA-20210902-x86_64-5-Hourly2-GP2",
    "RHEL_HA-8.5_HVM-20220127-x86_64-3-Hourly2-GP2",
    "RHEL_HA-8.6.0_HVM-20220503-x86_64-2-Hourly2-GP2",
    "RHEL_HA-8.6.0_HVM-20230118-x86_64-30-Hourly2-GP2",
    "RHEL_HA-8.6.0_HVM-20230301-x86_64-0-Hourly2-GP2",
    "RHEL_HA-8.6.0_HVM-20230411-x86_64-60-Hourly2-GP2",
    "RHEL_HA-8.7.0_HVM-20221101-x86_64-0-Hourly2-GP2",
    "RHEL_HA-8.7.0_HVM-20230215-x86_64-13-Hourly2-GP2",
    "RHEL_HA-8.7.0_HVM-20230330-x86_64-56-Hourly2-GP2",
    "RHEL_HA-8.8.0_HVM-20230503-x86_64-54-Hourly2-GP2",
    "RHEL_HA-8.8.0_HVM-20230623-x86_64-3-Hourly2-GP2",
    "RHEL_HA-9.0.0_HVM-20220513-x86_64-0-Hourly2-GP2",
    "RHEL_HA-9.0.0_HVM-20221027-x86_64-1-Hourly2-GP2",
    "RHEL_HA-9.0.0_HVM-20230127-x86_64-24-Hourly2-GP2",
    "RHEL_HA-9.0.0_HVM-20230313-x86_64-43-Hourly2-GP2",
    "RHEL_HA-9.0.0_HVM-20230418-x86_64-6-Hourly2-GP2",
    "RHEL_HA-9.0.0_HVM-20230531-x86_64-4-Hourly2-GP2",
    "RHEL_HA-9.0.0_HVM_BETA-20211026-x86_64-10-Hourly2-GP2",
    "RHEL_HA-9.1.0_HVM-20221101-x86_64-2-Hourly2-GP2",
    "RHEL_HA-9.1.0_HVM-20230222-x86_64-39-Hourly2-GP2",
    "RHEL_HA-9.1.0_HVM-20230404-x86_64-54-Hourly2-GP2",
    "RHEL_HA-9.2.0_HVM-20230503-x86_64-41-Hourly2-GP2",
    "RHEL_HA-9.2.0_HVM-20230615-x86_64-3-Hourly2-GP2",
    "RHEL-SAP-8.1.0_HVM-20211007-x86_64-0-Hourly2-GP2",
    "RHEL-SAP-8.2.0_HVM-20211007-x86_64-0-Hourly2-GP2",
]

SAMPLE_AWS_IMAGE_RECORD = {
    "Architecture": "x86_64",
    "CreationDate": "2023-06-16T04:56:41.000Z",
    "ImageId": "ami-0885899fb6698d6c7",
    "ImageLocation": "amazon/RHEL_HA-9.2.0_HVM-20230615-x86_64-3-Hourly2-GP2",
    "ImageType": "machine",
    "Public": True,
    "OwnerId": "309956199498",
    "PlatformDetails": "Red Hat Enterprise Linux with High Availability",
    "UsageOperation": "RunInstances:1010",
    "State": "available",
    "Description": "Provided by Red Hat, Inc.",
    "EnaSupport": True,
    "Hypervisor": "xen",
    "ImageOwnerAlias": "amazon",
    "Name": "RHEL_HA-9.2.0_HVM-20230615-x86_64-3-Hourly2-GP2",
    "RootDeviceName": "/dev/sda1",
    "RootDeviceType": "ebs",
    "SriovNetSupport": "simple",
    "VirtualizationType": "hvm",
    "DeprecationTime": "2025-06-16T04:56:41.000Z",
}


@pytest.mark.parametrize("image_name", AWS_NAMES)
def test_parsing_image_name(image_name: str) -> None:
    """Ensure we can parse AWS image names."""
    result = format_aws.parse_image_name_rhel(image_name)
    assert isinstance(result, dict)

    # All images carry the same keys for some things.
    assert result["storage"] == "GP2"
    assert result["billing"] == "Hourly2"

    # The release should be a number.
    assert int(result["release"]) >= 0

    # Architectures can only be one of two options.
    assert result["arch"] in ["x86_64", "arm64"]

    # Dates should be 8 digit YYYYMMDD.
    assert len(result["date"]) == 8

    # Internal/external product names must be a limited set.
    assert result["intprod"] in ["", "HA"]
    assert result["extprod"] in ["", "SAP"]

    assert re.match(r"\d\.\d(\.\d)*", result["version"])


def test_parsing_image_name_ugly() -> None:
    """Test parsing an image name that does not match our criteria."""
    image_name = "monkey-pizza-2479-😄"
    result = format_aws.parse_image_name_rhel(image_name)
    assert result == {}


def test_image_rhel() -> None:
    """Ensure we can handle the parsed image data."""
    result = format_aws.image_rhel(SAMPLE_AWS_IMAGE_RECORD, "us-east-1")

    assert isinstance(result, dict)
    assert result["name"] == "RHEL 9.2.0 HA hvm x86_64 Hourly2"
    assert result["arch"] == "x86_64"
    assert result["version"] == "9.2.0"
    assert result["imageId"] == "ami-0885899fb6698d6c7"
    assert result["date"] == "2023-06-16T04:56:41.000Z"
    assert result["virt"] == "hvm"
    assert (
        result["selflink"] == "https://console.aws.amazon.com/ec2/home?region=us-east-1#launchAmi=ami-0885899fb6698d6c7"
    )
    assert result["region"] == "us-east-1"
