"""Test image updates from remote cloud APIs."""
from __future__ import annotations

from unittest.mock import patch

from src.rhelocator import update_images


def test_get_aws_regions():
    """Test AWS region request."""
    with patch("botocore.client.BaseClient._make_api_call") as boto:
        update_images.get_aws_regions()

    boto.assert_called_with("DescribeRegions", {"AllRegions": "True"})


def test_get_aws_cloud_access_images():
    """Test AWS image request."""
    with patch("botocore.client.BaseClient._make_api_call") as boto:
        update_images.get_aws_cloud_access_images("us-east-1")

    boto.assert_called_with(
        "DescribeImages", {"IncludeDeprecated": "False", "Owners": ["309956199498"]}
    )
