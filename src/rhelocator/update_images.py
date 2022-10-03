"""Update images from public cloud APIs."""
from __future__ import annotations

import boto3


def get_aws_regions() -> list[str]:
    """Get the latest list of AWS regions.

    Returns:
        List of AWS regions as strings.
    """
    ec2 = boto3.client("ec2", region_name="us-east-1")
    raw = ec2.describe_regions(AllRegions="True")
    return [x["RegionName"] for x in raw["Regions"]]


def get_aws_cloud_access_images(region: str) -> list[str]:
    """Get a list of RHEL cloud access images from an AWS region.

    Args:
        region: AWS region name, such as us-east-1
    """
    ec2 = boto3.client("ec2", region_name=region)
    raw = ec2.describe_images(Owners=["309956199498"], IncludeDeprecated="False")
    return list(raw["Images"])
