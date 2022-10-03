"""Test image updates from remote cloud APIs."""
from __future__ import annotations

from unittest import mock

from src.rhelocator import update_images


@mock.patch("botocore.client.BaseClient._make_api_call")
def test_get_aws_regions(mock_boto: any):
    """Test AWS region request."""
    with mock.patch("botocore.client.BaseClient._make_api_call") as boto:
        update_images.get_aws_regions()

    boto.assert_called_with("DescribeRegions", {"AllRegions": "True"})


@mock.patch("botocore.client.BaseClient._make_api_call")
def test_get_aws_cloud_access_images(mock_boto: any):
    """Test AWS image request."""
    with mock.patch("botocore.client.BaseClient._make_api_call") as boto:
        update_images.get_aws_cloud_access_images("us-east-1")

    boto.assert_called_with(
        "DescribeImages", {"IncludeDeprecated": "False", "Owners": ["309956199498"]}
    )
