"""Update images from public cloud APIs."""
from __future__ import annotations

import re

from typing import Any

from google.cloud import compute_v1

from cloudimagedirectory import config


def get_images() -> list[dict[str, str]]:
    """Get a list of RHEL images from Google Cloud.

    Returns:
        List of Google Compute image names.
    """
    images_client = compute_v1.ImagesClient()

    # NOTE(mhayden): Google's examples suggest using a filter here for "deprecated.state
    # != DEPRECATED" but it returns no images when I tried it.
    # https://github.com/googleapis/python-compute/blob/main/samples/recipes/images/pagination.py
    images_list_requests = []

    for projectname in config.GOOGLE_PROJECTNAME:
        images_list_requests.append(compute_v1.ListImagesRequest(project=projectname))

    # Normalize the data first.
    normalized_image_list: list[dict[str, str]] = []
    for request in images_list_requests:
        normalized_image_list.extend(
            normalize_google_images(
                [
                    x
                    for x in images_client.list(request=request)
                    if x.deprecated.state != "DEPRECATED"
                ]
            )
        )
    return normalized_image_list


def normalize_google_images(image_list: list[Any]) -> list[dict[str, str]]:
    """Normalize the data returned from Google's image listing.

    The GOOGLE SDK returns an unusual object with repeated attributes and some
    attributes lead to other interesting objects. The goal here is to normalize
    this data so that it's dict-like, similar to the Azure and AWS functions.

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


def parse_image_name(image_name: str) -> dict[str, str]:
    """Parse an google image name and return version string.

    Regex101: https://regex101.com/r/9QCWIJ/1

    Args:
        image_name: String containing the image name, such as:
                    rhel-7-9-sap-v20220719

    Returns:
        Dictionary with additional information about the image.
    """
    google_image_name_regex = (
        r"(?P<product>\w*)-(?P<version>[\d]+(?:\-[\d]){0,3})-?"
        r"(?P<extprod>\w*)?-v(?P<date>\d{4}\d{2}\d{2})"
    )

    matches = re.match(google_image_name_regex, image_name, re.IGNORECASE)
    if matches:
        return matches.groupdict()

    return {}


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
    additional_information = parse_image_name(image["name"])

    arch = image["architecture"]
    image_id = image["name"]
    date = image["creation_timestamp"]
    extprod = additional_information["extprod"]
    version = additional_information["version"].replace("-", ".")

    name_parts = ["RHEL", version, extprod]

    # This is necessary to avoid creating names like "RHEL 9 arm64 arm64"
    # as the naming conventions for Google images are inconsistent.
    # e.g.
    # rhel-9-arm64-v20221206
    # rhel-7-6-sap-v20221102
    if extprod.lower() != arch.lower():
        name_parts.append(arch)

    name = " ".join([x for x in name_parts if x != ""])

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
