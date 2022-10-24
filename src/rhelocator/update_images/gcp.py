"""Update images from public cloud APIs."""
from __future__ import annotations

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
