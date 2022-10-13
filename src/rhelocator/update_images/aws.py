"""Update images from public cloud APIs."""
from __future__ import annotations

import re

import boto3

from rhelocator import config


def get_aws_regions() -> list[str]:
    """Get the latest list of AWS regions.

    Returns:
        List of AWS regions as strings.
    """
    ec2 = boto3.client("ec2", region_name="us-east-1")
    # TODO(mhayden): Remove the opt-in-status filter below once AWS enables the
    #  additional regions for the account. The opt-in was requested on 2022-10-11 but
    #  it could take time before they are enabled.
    raw = ec2.describe_regions(
        Filters=[
            {"Name": "opt-in-status", "Values": ["opt-in-not-required", "opted-in"]}
        ],
        AllRegions=True,
    )
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


def parse_aws_image_name(image_name: str) -> dict[str, str]:
    """Parse an AWS image name and return extra data about the image.

    Regex101: https://regex101.com/r/mXCl73/1

    Args:
        image_name: String containing the image name, such as:
                    RHEL-9.0.0_HVM_BETA-20211026-x86_64-10-Hourly2-GP2

    Returns:
        Dictionary with additional information about the image.
    """
    # See Regex101 link above to tinker with this regex. Each group is named to make
    # it easier to handle parsed data. Explanation of names:
    #
    #     intprod = internal product (such as HA)
    #     extprod = external product (such as SAP)
    #     version = RHEL version (such as 9.0.0)
    #     virt = virtualization type (such as HVM)
    #     beta = beta vs non-beta release
    #     date = date image was produced
    #     arch = architecture (such as x86_64 or arm64)
    #     release = release number of the image
    #     billing = Hourly2 or Access2  #noqa: E800
    #     storage = storage type (almost always GP2)
    #
    aws_image_name_regex = (
        r"RHEL_*(?P<intprod>\w*)?-*(?P<extprod>\w*)?-(?P<version>[\d\-\.]*)_"
        r"(?P<virt>[A-Z]*)_*(?P<beta>\w*)?-(?P<date>\d+)-(?P<arch>\w*)-"
        r"(?P<release>\d+)-(?P<billing>[\w\d]*)-(?P<storage>\w*)"
    )
    matches = re.match(aws_image_name_regex, image_name, re.IGNORECASE)
    if matches:
        return matches.groupdict()

    return {}
