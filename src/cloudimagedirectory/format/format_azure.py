import re
from datetime import datetime

def parse_image_version_rhel(image_version: str) -> dict[str, str]:
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


def convert_date_rhel(date: str) -> str:
    """Convert timestamp to date string This fallback is necessary as Azure
    timestamps are inconsistent and can either follow yyyymmdd or yyyyddmm.

    Returns:
        Date as string following the structure "%Y-%m-%d"
    """
    try:
        return datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")
    except:
        return datetime.strptime(date, "%Y%d%m").strftime("%Y-%m-%d")

def image_rhel(image: dict[str, str]) -> dict[str, str]:
    """Compile a dictionary of important image information.

    Args:
        images: A dictionary containing metadata about the image.

    Returns:
        JSON like structure containing streamlined image
        information.
    """
    additional_information = parse_image_version_rhel(image["version"])

    arch = image["architecture"]
    image_id = image["urn"]
    virt_type = image["hyperVGeneration"]
    sku = image["sku"]
    offer = image["offer"]

    date = convert_date_rhel(additional_information["date"])
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
