import json

from flasgger import Swagger
from flask import Flask
from flask_cors import CORS

from rhelocator.api.routes.aws import aws_blueprint
from rhelocator.api.routes.azure import azure_blueprint
from rhelocator.api.routes.gcp import gcp_blueprint
from rhelocator.update_images import schema


def create_app(file_path: str) -> Flask:
    """Creates and returns a Flask server configuration including cloud image
    data.

    Args:
        data_path: String, path to image data JSON file.

    Returns: A FLask instance
    """
    app = Flask(__name__)

    app.config["SWAGGER"] = {
        "title": "Cloud Image Locator",
    }
    Swagger(app)

    CORS(app)

    # Add support for .env parsing:
    app.config.from_pyfile("config.py")

    with open(file_path) as f:
        image_data = json.load(f)
    schema.validate_json(image_data)

    app.register_blueprint(
        azure_blueprint(image_data["images"]["azure"]), url_prefix="/api"
    )

    app.register_blueprint(
        gcp_blueprint(image_data["images"]["google"]), url_prefix="/api"
    )

    app.register_blueprint(
        aws_blueprint(image_data["images"]["aws"]), url_prefix="/api"
    )

    return app


def run(
    host: str = "0.0.0.0", port: int = 5000, file_path: str = "./image-data.json"
) -> None:
    """Run a Flask server on the provided host address, port serving the image
    data.

    Args:
        host: String, host address
        port: Int, Port
        file_path: String, path to image data JSON file
    """
    app = create_app(file_path)
    app.run(host=host, port=port)
