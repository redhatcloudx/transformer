"""Update images from public cloud APIs."""
from __future__ import annotations

import functools

import boto3
import requests

from rhelocator import config


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
        region: AWS region name, such as "us-east-1"

    Returns:
        List of dictionaries containing metadata about images.
    """
    ec2 = boto3.client("ec2", region_name=region)
    raw = ec2.describe_images(Owners=["309956199498"], IncludeDeprecated="False")
    return list(raw["Images"])


@functools.lru_cache
def get_azure_access_token() -> str:
    """Authenticate with Azure and return the access token to use with API requests.

    Returns:
        Access token as a string.
    """
    params = {
        "grant_type": "client_credentials",
        "client_id": config.AZURE_CLIENT_ID,
        "client_secret": config.AZURE_CLIENT_SECRET,
        "resource": "https://management.azure.com/",
    }
    url = f"https://login.microsoftonline.com/{config.AZURE_TENANT_ID}/oauth2/token"
    resp = requests.post(url, data=params, timeout=10)
    return str(resp.json().get("access_token", None))


def get_azure_locations(access_token: str) -> list[str]:
    """Get a list of all Azure locations.

    Azure API docs:
        https://learn.microsoft.com/en-us/rest/api/resources/subscriptions/list-locations?tabs=HTTP

    Args:
        access_token: Valid Azure access token from get_azure_access_token().

    Returns:
        List of valid Azure regions.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"api-version": "2020-01-01"}
    url = (
        f"https://management.azure.com/subscriptions/{config.AZURE_SUBSCRIPTION_ID}"
        "/locations"
    )
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    return sorted([x["name"] for x in resp.json()["value"]])
