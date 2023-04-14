import re


def parse_image_name_rhel(image_name: str) -> dict[str, str]:
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


def image_rhel(image: dict[str, str], region: str) -> dict[str, str]:
    """Compile a dictionary of important image information.

    Args:
        images: A dictionary containing metadata about the image.
        region: Name of the image region.

    Returns:
        JSON like structure containing streamlined image
        information.
    """
    additional_information = parse_image_name_rhel(image["Name"])

    arch = image["Architecture"]
    image_id = image["ImageId"]
    virt_type = image["VirtualizationType"]
    date = image["CreationDate"]
    version = additional_information["version"]
    beta = additional_information["beta"]
    billing = additional_information["billing"]
    extprod = additional_information["extprod"]
    intprod = additional_information["intprod"]
    name_parts = ["RHEL", version, intprod, extprod, virt_type, arch, billing, beta]

    name = " ".join([x for x in name_parts if x != ""])
    selflink = (
        f"https://console.aws.amazon.com/ec2/home?region={region}#launchAmi={image_id}"
    )

    return {
        "name": name,
        "arch": arch,
        "version": version,
        "imageId": image_id,
        "date": date,
        "virt": virt_type,
        "selflink": selflink,
        "region": region,
    }
