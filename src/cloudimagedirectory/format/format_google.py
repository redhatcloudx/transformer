import re

def parse_image_name_rhel(image_name: str) -> dict[str, str]:
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

def image_rhel(image: dict[str, str]) -> dict[str, str]:
    """Compile a dictionary of important image information.

    Args:
        images: A dictionary containing metadata about the image.

    Returns:
        JSON like structure containing streamlined image
        information.
    """
    additional_information = parse_image_name_rhel(image["name"])

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
