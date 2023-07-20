from dataclasses import dataclass


class InvalidSelfLink(Exception):
    """Raised exception when a self link is invalid."""

    def __init__(self) -> None:
        """Constructor for InvalidSelfLink class."""
        super().__init__("Invalid selflink")


@dataclass
class GoogleRHELParser:
    """Parse a Google RHEL image name."""

    image_name: str

    # TODO: We should probably uppercase this in the future since SAP is always uppercase.
    @property
    def extprod(self) -> str:
        """
        Return the external product name.

        The second to last piece could contain a few different things:
        1) The whole version number
        2) The second half of the version number
        3) The architecture
        4) The external product name.
        """
        piece = self.image_name.split("-")[-2]

        # Get rid of version numbers or architecture strings.
        if piece.isdigit() or piece in ["arm64", "x86_64"]:
            return ""

        return piece

    @property
    def product(self) -> str:
        """Return the product name."""
        return str(self.image_name.split("-")[0])

    @property
    def version(self) -> str:
        """
        Return the product version.

        The version can be a single number, such as "8", but it can also be two numbers separate by dashes, like "9-2".
        """
        version_pieces = self.image_name.split("-")[1:3]

        # Do we have two numbers separated by a dash?
        if version_pieces[1].isdigit():
            return f"{version_pieces[0]}.{version_pieces[1]}"

        # We have a single version number.
        return str(version_pieces[0])


def google_extract_project_name(selflink: str) -> str:
    """Extract the project name from a selflink."""
    selflink_list = selflink.split("/")
    if len(selflink_list) < 7 or selflink_list[5] != "projects":
        # NOTE: We extract the current project name from the original selflink.
        # Example selflinks:
        # https://.../compute/imagesDetail/projects/rhel-cloud/.../...
        # https://.../compute/imagesDetail/projects/rhel-sap-cloud/.../...
        raise InvalidSelfLink()

    return selflink.split("/")[6]


def google_selflink(selflink: str) -> str:
    """Verify that we can create a valid direct link from Google's API link."""
    project_name = google_extract_project_name(selflink)
    image_name = selflink.split("/")[-1]
    return f"https://console.cloud.google.com/compute/imagesDetail/projects/{project_name}/global/images/{image_name}"


def image_rhel(image: dict[str, str]) -> dict[str, str]:
    """Compile a dictionary of important image information.

    Args:
        images: A dictionary containing metadata about the image.

    Returns:
        JSON like structure containing streamlined image
        information.
    """
    parsed = GoogleRHELParser(image["name"])

    # Build a friendly name for the image and skip the extprod if it isn't present.
    name_parts = ["RHEL", parsed.version, parsed.extprod, image["architecture"]]
    name = " ".join([x for x in name_parts if x != ""])

    return {
        "name": name,
        "arch": image["architecture"],
        "version": parsed.version,
        "imageId": image["selfLink"],
        "date": image["creation_timestamp"],
        "selflink": google_selflink(image["selfLink"]),
    }
