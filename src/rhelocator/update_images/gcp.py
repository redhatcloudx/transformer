"""Update images from public cloud APIs."""
from __future__ import annotations

import re

from typing import Any

from google.cloud import compute_v1

from rhelocator import config


def get_images() -> list[dict[str, str]]:
    """Get a list of RHEL images from Google Cloud.

    Returns:
        List of Google Compute image names.
    """
    images_client = compute_v1.ImagesClient()

    # NOTE(mhayden): Google's examples suggest using a filter here for "deprecated.state
    # != DEPRECATED" but it returns no images when I tried it.
    # https://github.com/googleapis/python-compute/blob/main/samples/recipes/images/pagination.py
    images_list_request = compute_v1.ListImagesRequest(project=config.GCP_PROJECTNAME)

    # Normalize the data first.

    return normalize_google_images(
        [
            x
            for x in images_client.list(request=images_list_request)
            if x.deprecated.state != "DEPRECATED"
        ]
    )


def normalize_google_images(image_list: list[Any]) -> list[dict[str, str]]:
    """Normalize the data returned from Google's image listing.

    The GCP SDK returns an unusual object with repeated attributes and some attributes
    lead to other interesting objects. The goal here is to normalize this data so that
    it's dict-like, similar to the Azure and AWS functions.

    Args:
        image_list: A Google image listing from the ImagesClient class.

    Returns:
        List of dictionaries containing normalized image data.
    """
    normalized_images = []

    for img in image_list:
        image_data = {
            "architecture": img.architecture.lower(),
            "creation_timestamp": img.creation_timestamp,
            "description": img.description,
            "name": img.name,
        }
        normalized_images.append(image_data)

    return normalized_images


def parse_image_version_from_name(image_name: str) -> str:
    """Parse an google image name and return version string.

    Regex101: https://regex101.com/r/CiABs5/1

    Args:
        image_name: String containing the image name, such as:
                    rhel-7-9-sap-v20220719

    Returns:
        Returns the google image version as string
                    rhel-7-9
    """
    google_image_name_regex = (
        r"(?P<product>\w*)-(?P<version>[\d]+(?:\-[\d]){0,3})-?"
        r"(?P<intprod>\w*)?-v(?P<date>\d{4}\d{2}\d{2})"
    )

    matches = re.match(google_image_name_regex, image_name, re.IGNORECASE)
    if matches:
        image_data = matches.groupdict()
        version = image_data["version"]
        return version.replace("-", ".")
    return "unknown"


def format_all_images() -> object:
    """Retrieve all google images and return a simplified data representation.

    Returns:
        JSON like structure containting a list of streamlined image
        information.
    """
    formatted_images: list[dict[str, str]] = []

    images = get_images()

    for image in images:
        formatted_images.append(format_image(image))

    return {"images": {"google": formatted_images}}


def format_image(image: dict[str, str]) -> dict[str, str]:
    """Compile a dictionary of important image information.

    Args:
        images: A dictionary containing metadata about the image.

    Returns:
        JSON like structure containing streamlined image
        information.
    """

    arch = image["architecture"]
    image_id = image["name"]
    date = image["creation_timestamp"]
    version = parse_image_version_from_name(image["name"])

    name = f"RHEL {version} {arch}"
    selflink = "https://console.cloud.google.com/compute/imagesDetail/"
    selflink += f"projects/rhel-cloud/global/images/{image_id}"

    return {
        "name": name,
        "arch": arch,
        "version": version,
        "imageId": image_id,
        "date": date,
        "selflink": selflink,
    }
