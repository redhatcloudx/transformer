"""Update images from public cloud APIs."""
from __future__ import annotations

from google.cloud import compute_v1

from rhelocator import config


def get_google_images() -> list[str]:
    """Get a list of RHEL images from Google Cloud.

    Returns:
        List of Google Compute image names.
    """
    images_client = compute_v1.ImagesClient()
    # NOTE(mhayden): Google's examples suggest using a filter here for "deprecated.state
    # != DEPRECATED" but it returns no images when I tried it.
    # https://github.com/googleapis/python-compute/blob/main/samples/recipes/images/pagination.py
    images_list_request = compute_v1.ListImagesRequest(project=config.GCP_PROJECTNAME)

    return [
        x.name
        for x in images_client.list(request=images_list_request)
        if x.deprecated.state != "DEPRECATED"
    ]
