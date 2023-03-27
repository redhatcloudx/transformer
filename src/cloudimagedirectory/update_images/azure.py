"""Update images from public cloud APIs."""
from __future__ import annotations

import re
import time

from datetime import datetime

import requests
import structlog

from requests import HTTPError
from requests import RequestException
from requests import Timeout
from requests import TooManyRedirects

from cloudimagedirectory import config


logger = structlog.get_logger()


def post_request(url: str, params: dict[str, str | None]) -> requests.Response:
    try:
        return requests.post(url, params, timeout=10)
    except Timeout:
        logger.warning(f"Timeout trying to reach: {url}")
        return requests.Response()
    except (HTTPError, TooManyRedirects, RequestException, Exception) as err:
        logger.critical(f"Encountered critical error: {err}")
        raise SystemExit(err)


def get_request(
    url: str, params: dict[str, str], headers: dict[str, str]
) -> requests.Response:
    try:
        return requests.get(url, params=params, headers=headers, timeout=10)
    except Timeout:
        logger.warning(f"Timeout trying to reach: {url}")
        return requests.Response()
    except (HTTPError, TooManyRedirects, RequestException, Exception) as err:
        logger.critical(f"Encountered critical error: {err}")
        raise SystemExit(err)


def get_access_token() -> str:
    """Authenticate with Azure and return the access token to use with API
    requests.

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

    for _i in range(config.AZURE_MAX_RETRIES):
        resp = post_request(url, params)

        if resp.status_code == 200:
            return str(resp.json().get("access_token", None))

        logger.warning(f"Retry conneting to {url}")
        time.sleep(config.AZURE_REQUEST_FAILURE_TIMEOUT)

    # If no auth token can be obtained, throw an exception.
    raise Exception("Unable to authenticate.")


def get_locations(access_token: str) -> list[str]:
    """Get a list of all Azure locations.

    https://learn.microsoft.com/en-us/rest/api/resources/subscriptions/list-locations?tabs=HTTP

    Returns:
        List of valid Azure regions.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"api-version": "2020-01-01"}
    url = (
        f"https://management.azure.com/subscriptions/{config.AZURE_SUBSCRIPTION_ID}"
        "/locations"
    )
    resp = None
    for _i in range(config.AZURE_MAX_RETRIES):
        resp = get_request(url, params, headers)
        if resp.status_code == 200:
            return sorted([x["name"] for x in resp.json()["value"]])

        logger.warning(f"Retry conneting to {url}")
        time.sleep(config.AZURE_REQUEST_FAILURE_TIMEOUT)

    raise Exception("Unable to retrieve locations.")


def get_publishers(access_token: str, location: str) -> list[str]:
    """Get a list of Azure publishers.

    Publishers create offers (which contain SKUs and image versions).
    https://learn.microsoft.com/en-us/rest/api/compute/virtual-machine-images/list-publishers

    Args:
        location: String containing a valid Azure location, such as eastus

    Returns:
        List of publishers on Azure.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"api-version": "2022-08-01"}
    url = (
        f"https://management.azure.com/subscriptions/{config.AZURE_SUBSCRIPTION_ID}/"
        f"providers/Microsoft.Compute/locations/{location}/publishers"
    )
    resp = None
    for _i in range(config.AZURE_MAX_RETRIES):
        resp = get_request(url, params, headers)
        if resp.status_code == 200:
            return sorted([x["name"] for x in resp.json()])

        logger.warning(f"Retry conneting to {url}")
        time.sleep(config.AZURE_REQUEST_FAILURE_TIMEOUT)

    raise Exception("Unable to retrieve publishers.")


def get_offers(access_token: str, location: str, publisher: str) -> list[str]:
    """Get a list of Azure offers.

    Offers come from a publisher and each offer contains one or more SKUs.
    https://learn.microsoft.com/en-us/rest/api/compute/virtual-machine-images/list-offers?tabs=HTTP

    Args:
        location: String containing a valid Azure location, such as eastus
        publisher: String containing an Azure publisher, such as redhat

    Returns:
        List of offers on Azure.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"api-version": "2022-08-01"}
    url = (
        f"https://management.azure.com/subscriptions/{config.AZURE_SUBSCRIPTION_ID}/"
        f"providers/Microsoft.Compute/locations/{location}/publishers/"
        f"{publisher}/artifacttypes/vmimage/offers"
    )
    resp = None
    for _i in range(config.AZURE_MAX_RETRIES):
        resp = get_request(url, params, headers)
        if resp.status_code == 200:
            return sorted([x["name"] for x in resp.json()])

        logger.warning(f"Retry conneting to {url}")
        time.sleep(config.AZURE_REQUEST_FAILURE_TIMEOUT)

    raise Exception("Unable to retrieve offers.")


def get_skus(access_token: str, location: str, publisher: str, offer: str) -> list[str]:
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
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"api-version": "2022-08-01"}
    url = (
        f"https://management.azure.com/subscriptions/{config.AZURE_SUBSCRIPTION_ID}/"
        f"providers/Microsoft.Compute/locations/{location}/publishers/"
        f"{publisher}/artifacttypes/vmimage/offers/{offer}/skus"
    )
    resp = None
    for _i in range(config.AZURE_MAX_RETRIES):
        resp = get_request(url, params, headers)
        if resp.status_code == 200:
            return sorted([x["name"] for x in resp.json()])

        logger.warning(f"Retry conneting to {url}")
        time.sleep(config.AZURE_REQUEST_FAILURE_TIMEOUT)

    raise Exception("Unable to retrieve skus.")


def get_image_versions(
    access_token: str,
    location: str,
    publisher: str,
    offer: str,
    sku: str,
    latest: bool = True,
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
        List of names on Azure.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"api-version": "2022-08-01"}
    url = (
        f"https://management.azure.com/subscriptions/{config.AZURE_SUBSCRIPTION_ID}/"
        f"providers/Microsoft.Compute/locations/{location}/publishers/"
        f"{publisher}/artifacttypes/vmimage/offers/{offer}/skus/{sku}/versions"
    )
    resp = None
    for _i in range(config.AZURE_MAX_RETRIES):
        resp = get_request(url, params, headers)
        if resp.status_code == 200:
            images = [x["name"] for x in resp.json()]

            # Return only the last image if requested.
            if latest:
                return [images[-1]]

            return images

        logger.warning(f"Retry conneting to {url}")
        time.sleep(config.AZURE_REQUEST_FAILURE_TIMEOUT)

    raise Exception("Unable to retrieve image versions.")


def get_image_details(
    access_token: str, location: str, publisher: str, offer: str, sku: str, version: str
) -> dict[str, dict[str, str]]:
    """Get details about a specific image.

    Args:
        location: String containing a valid Azure location, such as eastus
        publisher: String containing an Azure publisher, such as redhat
        offer: String container an offer name
        sku: String containing a SKU name
        version: String containing a valid image SKU version

    Returns:
        Dictionary of image details
    """

    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"api-version": "2022-08-01"}

    url = (
        f"https://management.azure.com/subscriptions/{config.AZURE_SUBSCRIPTION_ID}/"
        f"providers/Microsoft.Compute/locations/{location}/publishers/"
        f"{publisher}/artifacttypes/vmimage/offers/{offer}/skus/{sku}/"
        f"versions/{version}"
    )

    resp = None
    for _i in range(config.AZURE_MAX_RETRIES):
        resp = get_request(url, params, headers)
        if resp.status_code == 200:
            data: dict[str, dict[str, str]] = resp.json()
            return data

        logger.warning(f"Retry conneting to {url}")
        time.sleep(config.AZURE_REQUEST_FAILURE_TIMEOUT)

    raise Exception("Unable to retrieve image details.")


def get_images() -> list[dict[str, str]]:
    """Get a list of Azure RHEL images.

    Returns:
        List of dictionaries matching `az vm image list` output.
    """
    results = []
    access_token = get_access_token()
    for entry in config.AZURE_RHEL_IMAGE_TREE:
        for publisher, offers in entry.items():
            for offer, skus in offers.items():
                for sku, version in skus.items():
                    # Are we looking for the latest image or all images?
                    latest = True
                    if version != "latest":
                        latest = False
                    # Get the image versions that match the pub/offer/sku combination.
                    image_versions = get_image_versions(
                        access_token,
                        config.AZURE_DEFAULT_LOCATION,
                        publisher,
                        offer,
                        sku,
                        latest,
                    )

                    # Loop through the image versions and add on this image version to
                    # the list in Azure's `az vm image list` format.
                    for image_version in image_versions:
                        image_details = get_image_details(
                            access_token,
                            config.AZURE_DEFAULT_LOCATION,
                            publisher,
                            offer,
                            sku,
                            image_version,
                        )
                        hypervgen = image_details["properties"].get(
                            "hyperVGeneration", "unknown"
                        )
                        arch = image_details["properties"].get(
                            "architecture", "unknown"
                        )

                        result = {
                            "architecture": arch,
                            "hyperVGeneration": hypervgen,
                            "offer": offer,
                            "publisher": publisher,
                            "sku": sku,
                            "urn": f"{publisher}:{offer}:{sku}:{image_version}",
                            "version": image_version,
                        }

                        results.append(result)

    return results


def parse_image_version(image_version: str) -> dict[str, str]:
    """Parse an AWS image name and return extra data about the image.

    Regex101: https://regex101.com/r/yHB9jJ/1

    Args:
        image_version: String containing the image version, such as:
                    7.4.2021051102 or 9.0.0.2022053014

    Returns:
        Dictionary with additional information about the image.
    """
    # See Regex101 link above to tinker with this regex. Each group is named to make
    # it easier to handle parsed data. Explanation of names:
    #
    #     version = RHEL version (such as 9.0)
    #     date = date image was produced
    #
    aws_image_name_regex = (
        r"(?P<version>[\d]+\.[\d]+(?:\.[\d]+)?)\.(?P<date>\d{4}\d{2}\d{2})"
    )
    matches = re.match(aws_image_name_regex, image_version, re.IGNORECASE)
    if matches:
        return matches.groupdict()

    return {}


def convert_date(date: str) -> str:
    """Convert timestamp to date string This fallback is necessary as Azure
    timestamps are inconsistent and can either follow yyyymmdd or yyyyddmm.

    Returns:
        Date as string following the structure "%Y-%m-%d"
    """
    try:
        return datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")
    except:
        return datetime.strptime(date, "%Y%d%m").strftime("%Y-%m-%d")


def format_all_images() -> object:
    """Retrieve all Azure images and return a simplified data representation.

    Returns:
        JSON like structure containting a list of streamlined image information.
    """
    formatted_images: list[dict[str, str]] = []

    images = get_images()

    for image in images:
        formatted_images.append(format_image(image))

    return {"images": {"azure": formatted_images}}


def format_image(image: dict[str, str]) -> dict[str, str]:
    """Compile a dictionary of important image information.

    Args:
        images: A dictionary containing metadata about the image.

    Returns:
        JSON like structure containing streamlined image
        information.
    """

    additional_information = parse_image_version(image["version"])

    arch = image["architecture"]
    image_id = image["urn"]
    virt_type = image["hyperVGeneration"]
    sku = image["sku"]
    offer = image["offer"]

    date = convert_date(additional_information["date"])
    version = additional_information["version"]

    name = f"{offer} {sku} {arch}"

    return {
        "name": name,
        "arch": arch,
        "version": version,
        "imageId": image_id,
        "date": date,
        "virt": virt_type,
    }
