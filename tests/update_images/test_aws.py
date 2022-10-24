"""Test image updates from remote cloud APIs."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from rhelocator import config
from rhelocator.update_images import aws


def test_get_regions() -> None:
    """Test AWS region request."""
    with patch("botocore.client.BaseClient._make_api_call") as boto:
        aws.get_regions()

    boto.assert_called_with(
        "DescribeRegions",
        {
            "AllRegions": True,
            "Filters": [
                {"Name": "opt-in-status", "Values": ["opt-in-not-required", "opted-in"]}
            ],
        },
    )


def test_describe_images() -> None:
    """Test AWS image request."""
    with patch("botocore.client.BaseClient._make_api_call") as boto:
        aws.describe_images("us-east-1")

    boto.assert_called_with(
        "DescribeImages",
        {"IncludeDeprecated": False, "Owners": [config.AWS_RHEL_OWNER_ID]},
    )


def test_get_hourly_images(mock_aws_regions, mock_aws_images):
    """Ensure we filter for hourly images properly."""
    images = aws.get_images(region="us-east-1", image_type="hourly")

    billing_codes = {x["UsageOperation"] for x in images}
    assert billing_codes == {config.AWS_HOURLY_BILLING_CODE}


def test_get_cloud_access_images(mock_aws_regions, mock_aws_images):
    """Ensure we filter for cloud access images properly."""
    images = aws.get_images(region="us-east-1", image_type="cloudaccess")

    billing_codes = {x["UsageOperation"] for x in images}
    assert billing_codes == {config.AWS_CLOUD_ACCESS_BILLING_CODE}


def test_get_images_bogus_type(mock_aws_regions, mock_aws_images):
    """Test the exception if someone provides a bogus image type."""
    with pytest.raises(NotImplementedError):
        aws.get_images(region="us-east-1", image_type="doot")


def test_get_all_images(mock_aws_regions, mock_aws_images) -> None:
    """Test retrieving all AWS hourly images from all regions."""
    images = aws.get_all_images()

    # Regions should be in the keys.
    assert list(images.keys()) == mock_aws_regions.return_value

    # Each region should have only hourly image billing codes.
    for _region, image_list in images.items():
        billing_codes = {x["UsageOperation"] for x in image_list}
        assert billing_codes == {config.AWS_HOURLY_BILLING_CODE}


def test_parse_image_name_basic():
    """Test parsing an AWS image name with a very basic image."""
    image_name = "RHEL-7.9_HVM-20220512-x86_64-1-Hourly2-GP2"
    data = aws.parse_image_name(image_name)

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


def test_parse_image_name_beta():
    """Test parsing an AWS image name for a beta arm64 image."""
    image_name = "RHEL-9.1.0_HVM_BETA-20220829-arm64-0-Hourly2-GP2"
    data = aws.parse_image_name(image_name)

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


def test_parse_image_name_internal_product():
    """Test parsing an AWS image name with an internal product."""
    image_name = "RHEL_HA-8.5.0_HVM-20211103-x86_64-0-Hourly2-GP2"
    data = aws.parse_image_name(image_name)

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


def test_parse_image_name_external_product():
    """Test parsing an AWS image name for a beta arm64 image."""
    image_name = "RHEL-SAP-8.2.0_HVM-20211007-x86_64-0-Hourly2-GP2"
    data = aws.parse_image_name(image_name)

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
