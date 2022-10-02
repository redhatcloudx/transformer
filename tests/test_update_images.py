"""Test image updates from remote cloud APIs."""
from __future__ import annotations

from unittest import mock

from src.rhelocator import update_images


@mock.patch("botocore.client.BaseClient._make_api_call")
def test_get_aws_regions(mock_boto: any):
    """Test AWS region request."""
    mock_boto.return_value: dict = {
        "Regions": [
            {
                "Endpoint": "ec2.us-east-1.amazonaws.com",
                "RegionName": "us-east-1",
            },
        ]
    }

    regions = update_images.get_aws_regions()

    assert isinstance(regions, list)
    assert "us-east-1" in regions
