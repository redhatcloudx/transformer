from typing import Optional

from flasgger import swag_from
from flask import Blueprint
from flask import request


def gcp_blueprint(data: list[dict[str, str]]) -> Blueprint:
    """Creates and returns a Flask blueprint based that serves the provided
    image data.

    Args:
        data: Formatted image data dict.

    Returns:
        Flask blueprint serving the provided data.
    """
    gcp_endpoint = Blueprint("api", __name__)

    @gcp_endpoint.route("/gcp", methods=["GET"])
    @swag_from("../schema/gcp.yml")
    def endpoint() -> list[dict[str, str]]:
        """Cloud Image Locator GCP Endpoint Provides RHEL image data for Google
        Cloud."""

        query: dict[str, str] = {}
        name: Optional[str] = request.args.get("name")
        arch: Optional[str] = request.args.get("arch")
        image_id: Optional[str] = request.args.get("imageId")
        date: Optional[str] = request.args.get("date")
        version: Optional[str] = request.args.get("version")

        if name:
            query.update({"name": name})
        if arch:
            query.update({"arch": arch})
        if image_id:
            query.update({"imageId": image_id})
        if date:
            query.update({"date": date})
        if version:
            query.update({"version": version})

        if len(query) == 0:
            return data

        response: list[dict[str, str]] = []
        for image in data:
            add_image = True
            for key, value in query.items():
                if value not in image[key]:
                    add_image = False
                    break
            if add_image:
                response.append(image)
        return response

    return gcp_endpoint
