from __future__ import annotations

from jsonschema import Draft202012Validator
from jsonschema import SchemaError
from jsonschema import ValidationError


SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema#",
    "definitions": {
        "defaults": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Human readable image name"},
                "arch": {"type": "string", "description": "Architecture"},
                "version": {
                    "type": "string",
                    "description": "RHEL image version following MAJOR.MINOR.PATCH",
                },
                "imageId": {
                    "type": "string",
                    "description": "Image ID used for running the image",
                },
                "date": {
                    "type": "string",
                    "description": "Date of image release in international date format",
                },
                "virt": {"type": "string", "description": "Hypervisor Type"},
            },
        },
        "aws": {
            "type": "object",
            "description": "AWS RHEL Image Data",
            "$ref": "#/definitions/defaults",
            "properties": {
                "selflink": {
                    "description": "URL for direct access from cloud console",
                    "format": "uri",
                    "pattern": r"^https://console\.aws\.amazon\.com/ec2/home\?region=[a-z0-9-]*#launchAmi=ami-[a-z0-9]*",  # noqa: E501
                },
                "region": {
                    "type": "string",
                    "description": "Region of image availability",
                },
            },
            "required": [
                "name",
                "version",
                "imageId",
                "date",
                "virt",
                "selflink",
                "region",
            ],
        },
        "azure": {
            "type": "object",
            "description": "Azure RHEL Image Data",
            "$ref": "#/definitions/defaults",
            "required": ["name", "arch", "version", "imageId", "date", "virt"],
        },
        "google": {
            "type": "object",
            "description": "Google RHEL Image Data",
            "$ref": "#/definitions/defaults",
            "properties": {
                "selflink": {
                    "description": "URL for direct access from cloud console",
                    "format": "uri",
                    "pattern": r"^https://console.cloud.google.com/compute/imagesDetail/projects/rhel-cloud/global/images/[a-z0-9-]*",  # noqa: E501
                }
            },
            "required": ["name", "version", "imageId", "date", "virt", "selflink"],
        },
    },
    "additionalProperties": False,
    "required": ["images"],
    "description": "Prepared Image Date for cloud image locator",
    "$ref": "#/definitions/defaults",
    "properties": {
        "images": {
            "type": "object",
            "additionalProperties": False,
            "description": "Prepared Image Data",
            "minProperties": 1,
            "properties": {
                "aws": {"type": "array", "items": {"$ref": "#/definitions/aws"}},
                "azure": {"type": "array", "items": {"$ref": "#/definitions/azure"}},
                "google": {"type": "array", "items": {"$ref": "#/definitions/google"}},
            },
        }
    },
}


def validate_json(data: object) -> None:
    """Validate a JSON document against the schema.

    Args:
        data: JSON string to validate.

    Returns:
        None if the schema is valid, or raises a ValidationError if it is invalid.
    """
    try:
        validator = Draft202012Validator(SCHEMA)
        errors = sorted(
            validator.iter_errors(data),
            key=lambda e: e.path,  # type: ignore[no-any-return]
        )

        if errors:
            error_message = "Error validating image data: "
            for error in errors:
                error_message += f"[{error.schema_path}]: {error.message}; "
            raise ValidationError(message=error_message)

    except (ValidationError, SchemaError) as e:
        raise ValidationError(e.message)
