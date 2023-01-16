from typing import Optional

from flasgger import swag_from
from flask import Blueprint
from flask import request
from flask import Response


def health_blueprint(data: dict[str, str]) -> Blueprint:
    """Creates and returns a Flask blueprint that sanity checks the provided image data.

    Args:
        data: Formatted image data dict.

    Returns:
        statuscode and message that describes operational health.
    """
    health_endpoint = Blueprint("health_api", __name__)

    @health_endpoint.route("/health", methods=["GET"])
    @swag_from("../schema/health.yml")
    def endpoint() -> Response:
        """Cloud Image Directory health Endpoint sanity checks the provided image data."""
        
        #TODO: Check-(check the value that comes back, ... ?)
        message = "ok" 
        status = 200
        image_data_is_corrupt = False

        if data is None:
            image_data_is_corrupt = True

        if image_data_is_corrupt:
            message = "image data is corrupt"
            status = 500

        return Response("{'message':'"+ message +"'}", status=status, mimetype='application/json')



    return health_endpoint
