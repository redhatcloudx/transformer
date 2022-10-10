"""Update images from public cloud APIs."""
from __future__ import annotations

import boto3
import requests

from google.cloud import compute_v1

from rhelocator import config


def get_aws_regions() -> list[str]:
    """Get the latest list of AWS regions.

    Returns:
        List of AWS regions as strings.
    """
    ec2 = boto3.client("ec2", region_name="us-east-1")
    raw = ec2.describe_regions(AllRegions=True)
    return sorted([x["RegionName"] for x in raw["Regions"]])


def aws_describe_images(region: str) -> list[dict[str, str]]:
    """Make an API call to AWS to get a list of RHEL images in a region.

    Args:
        region: AWS region name, such as us-east-1

    Returns:
        List of dictionaries containing image data.
    """
    ec2 = boto3.client("ec2", region_name=region)
    raw = ec2.describe_images(
        Owners=[config.AWS_RHEL_OWNER_ID], IncludeDeprecated=False
    )
    return list(raw["Images"])


def get_aws_images(region: str, image_type: str = "hourly") -> list[dict[str, str]]:
    """Get a list of RHEL hourly images from an AWS region.

    Args:
        region: AWS region name, such as us-east-1
        image_type: hourly or cloudaccess

    Returns:
        List of dictionaries containing metadata about images.
    """
    # Determine the right billing code for the UsageOperation field.

    if image_type == "hourly":
        billing_code = config.AWS_HOURLY_BILLING_CODE
    elif image_type == "cloudaccess":
        billing_code = config.AWS_CLOUD_ACCESS_BILLING_CODE
    else:
        raise (NotImplementedError("Only hourly and cloudaccess types are supported."))

    # Filter the results based on the billing code of the image.
    images = aws_describe_images(region)
    return [x for x in images if x["UsageOperation"] == billing_code]


def get_aws_all_images(image_type: str = "hourly") -> dict[str, list[dict[str, str]]]:
    """Retrieve all RHEL images from all regions."""
    regions = get_aws_regions()
    images_per_region = {}
    for region in regions:
        images = get_aws_images(region, image_type=image_type)
        images_per_region[region] = images

    return images_per_region


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


def get_azure_locations() -> list[str]:
    """Get a list of all Azure locations.

    https://learn.microsoft.com/en-us/rest/api/resources/subscriptions/list-locations?tabs=HTTP

    Returns:
        List of valid Azure regions.
    """
    access_token = get_azure_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"api-version": "2020-01-01"}
    url = (
        f"https://management.azure.com/subscriptions/{config.AZURE_SUBSCRIPTION_ID}"
        "/locations"
    )
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    return sorted([x["name"] for x in resp.json()["value"]])


def get_azure_publishers(location: str) -> list[str]:
    """Get a list of Azure publishers.

    Publishers create offers (which contain SKUs and image versions).
    https://learn.microsoft.com/en-us/rest/api/compute/virtual-machine-images/list-publishers

    Args:
        location: String containing a valid Azure location, such as eastus

    Returns:
        List of publishers on Azure.
    """
    access_token = get_azure_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"api-version": "2022-08-01"}
    url = (
        f"https://management.azure.com/subscriptions/{config.AZURE_SUBSCRIPTION_ID}/"
        f"providers/Microsoft.Compute/locations/{location}/publishers"
    )
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    return sorted([x["name"] for x in resp.json()])


def get_azure_offers(location: str, publisher: str) -> list[str]:
    """Get a list of Azure offers.

    Offers come from a publisher and each offer contains one or more SKUs.
    https://learn.microsoft.com/en-us/rest/api/compute/virtual-machine-images/list-offers?tabs=HTTP

    Args:
        location: String containing a valid Azure location, such as eastus
        publisher: String containing an Azure publisher, such as redhat

    Returns:
        List of offers on Azure.
    """
    access_token = get_azure_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"api-version": "2022-08-01"}
    url = (
        f"https://management.azure.com/subscriptions/{config.AZURE_SUBSCRIPTION_ID}/"
        f"providers/Microsoft.Compute/locations/{location}/publishers/"
        f"{publisher}/artifacttypes/vmimage/offers"
    )
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    return sorted([x["name"] for x in resp.json()])


def get_azure_skus(location: str, publisher: str, offer: str) -> list[str]:
    """Get a list of Azure SKUs.

    SKUs contain one or more image versions.
    https://learn.microsoft.com/en-us/rest/api/compute/virtual-machine-images/list-skus?tabs=HTTP

    Args:
        location: String containing a valid Azure location, such as eastus
        publisher: String containing an Azure publisher, such as redhat
        offer: String container an offer name

    Returns:
        List of skus on Azure.
    """
    access_token = get_azure_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"api-version": "2022-08-01"}
    url = (
        f"https://management.azure.com/subscriptions/{config.AZURE_SUBSCRIPTION_ID}/"
        f"providers/Microsoft.Compute/locations/{location}/publishers/"
        f"{publisher}/artifacttypes/vmimage/offers/{offer}/skus"
    )
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    return sorted([x["name"] for x in resp.json()])


def get_azure_image_versions(
    location: str, publisher: str, offer: str, sku: str, latest: bool = True
) -> list[str]:
    """Get a list of Azure image versions.

    Image versions exist under a SKU and are sorted *oldest* first.
    https://learn.microsoft.com/en-us/rest/api/compute/virtual-machine-images/list-skus?tabs=HTTP

    Args:
        location: String containing a valid Azure location, such as eastus
        publisher: String containing an Azure publisher, such as redhat
        offer: String container an offer name
        sku: String containing a SKU name
        latest: Set to True to get the latest available image only, False to get all

    Returns:
        List of skus on Azure.
    """
    access_token = get_azure_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"api-version": "2022-08-01"}
    url = (
        f"https://management.azure.com/subscriptions/{config.AZURE_SUBSCRIPTION_ID}/"
        f"providers/Microsoft.Compute/locations/{location}/publishers/"
        f"{publisher}/artifacttypes/vmimage/offers/{offer}/skus/{sku}/versions"
    )
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    images = [x["name"] for x in resp.json()]

    # Return only the last image if requested.
    if latest:
        return [images[-1]]

    return images


def get_azure_images() -> list[dict[str, str]]:
    """Get a list of Azure RHEL images.

    Returns:
        List of dictionaries matching `az vm image list` output.
    """
    results = []
    for publisher, offers in config.AZURE_RHEL_IMAGE_TREE.items():
        for offer, skus in offers.items():
            for sku, version in skus.items():
                # Are we looking for the latest image or all images?
                latest = True
                if version != "latest":
                    latest = False
                # Get the image versions that match the pub/offer/sku combination.
                image_versions = get_azure_image_versions(
                    config.AZURE_DEFAULT_LOCATION, publisher, offer, sku, latest
                )

                # Loop through the image versions and add on this image version to the
                # list in Azure's `az vm image list` format.
                for image_version in image_versions:
                    result = {
                        "offer": offer,
                        "publisher": publisher,
                        "sku": sku,
                        "urn": f"{publisher}:{offer}:{sku}:{image_version}",
                        "version": image_version,
                    }
                    results.append(result)

    return results


def get_google_images() -> list[str]:
    """Get a list of RHEL images from Google Cloud.

    Returns:
        List of Google Compute image names.
    """
    images_client = compute_v1.ImagesClient()
    # NOTE(mhayden): Google's examples suggest using a filter here for "deprecated.state
    # != DEPRECATED" but it returns no images when I tried it.
    # https://github.com/googleapis/python-compute/blob/main/samples/recipes/images/pagination.py
    images_list_request = compute_v1.ListImagesRequest(project="rhel-cloud")

    return [
        x.name
        for x in images_client.list(request=images_list_request)
        if x.deprecated.state != "DEPRECATED"
    ]
