"""CLI for updating images and other routine tasks."""
from __future__ import annotations

import json

import click
import waitress

from cloud-image-directory import __version__
from cloud-image-directory.api import server
from cloud-image-directory.update_images import aws
from cloud-image-directory.update_images import azure
from cloud-image-directory.update_images import google
from cloud-image-directory.update_images import schema


@click.group()
@click.version_option(version=__version__)
def cli() -> None:
    """Quick test."""


@click.command()
@click.option(
    "--region", help="Select specific AWS region to query (optional).", type=str
)
def aws_hourly_images(region: str) -> None:
    """Dump AWS hourly images from a range of regions in JSON format.

    Returns images for all regions by default.
    """
    if region:
        # Is this a valid region?
        valid_regions = aws.get_regions()
        if region not in valid_regions:
            message = f"{region} is not valid. Valid regions include: \n\n  "
            message += "\n  ".join(valid_regions)
            raise click.UsageError(message)

        formatted_images: list[dict[str, str]] = []
        images = aws.get_images(region)
        for image in images:
            formatted_images.append(aws.format_image(image, region))
        dump_images({"images": {"aws": formatted_images}})
    else:
        dump_images(aws.format_all_images())


@click.command()
def aws_regions() -> None:
    """Get all valid AWS regions."""
    regions = aws.get_regions()
    click.echo(json.dumps(regions, indent=2))


@click.command()
def google_images() -> None:
    """Dump GOOGLE images for all regions in JSON format."""
    images = google.format_all_images()
    dump_images(images)


@click.command()
def azure_images() -> None:
    """Dump Azure images in JSON format."""
    images = azure.format_all_images()
    dump_images(images)


def dump_images(images: object) -> None:
    """Validate and dump image data in JSON format."""
    schema.validate_json(images)
    click.echo(json.dumps(images, indent=2))


@click.command()
@click.option("-f", "--file-path", help="Path to JSON image data file.", type=str)
@click.option(
    "-p", "--port", show_default=True, default=5000, help="Port to run Locator API at."
)
@click.option(
    "-h",
    "--host",
    show_default=True,
    default="0.0.0.0",
    help="Address to run Locator API at.",
)
@click.option(
    "-d",
    "--dev",
    is_flag=True,
    show_default=True,
    default=False,
    help="Run in development mode.",
)
def serve(file_path: str, port: int, host: str, dev: bool) -> None:
    """Host API endpoint to serve cloud provider image data."""
    if dev:
        server.run(file_path=file_path, port=port, host=host)
    else:
        waitress.serve(
            server.create_app(file_path=file_path), host=host, port=port, threads=4
        )


cli.add_command(aws_hourly_images)
cli.add_command(aws_regions)
cli.add_command(azure_images)
cli.add_command(google_images)
cli.add_command(serve)
