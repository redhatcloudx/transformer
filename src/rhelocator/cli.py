"""CLI for updating images and other routine tasks."""
from __future__ import annotations

import json

import click

from rhelocator import __version__
from rhelocator.update_images import aws
from rhelocator.update_images import azure
from rhelocator.update_images import gcp


@click.group()
@click.version_option(version=__version__)
def cli() -> None:
    """Quick test."""


@click.command()
@click.option("--region", help="AWS region to query (optional)", type=str)
def aws_hourly_images(region: str) -> None:
    """Dump AWS hourly images from a region in JSON format."""
    # Verify that the user provided a region.
    if not region:
        raise click.UsageError(
            "Provide a valid AWS region with --region, such as 'us-east-1'"
        )

    # Is this a valid region?
    valid_regions = aws.get_regions()
    if region not in valid_regions:
        message = f"{region} is not valid. Valid regions include: \n\n  "
        message += "\n  ".join(valid_regions)
        raise click.UsageError(message)

    images = aws.get_images(region)
    click.echo(json.dumps(images, indent=2))


@click.command()
def aws_regions() -> None:
    """Get all valid AWS regions."""
    regions = aws.get_regions()
    click.echo(json.dumps(regions, indent=2))


@click.command()
def gcp_images() -> None:
    """Dump GCP images for all regions in JSON format."""
    images = gcp.get_images()
    click.echo(json.dumps(images, indent=2))


@click.command()
def azure_images() -> None:
    """Dump Azure images from a region in JSON format."""
    images = azure.get_images()
    click.echo(json.dumps(images, indent=2))


cli.add_command(aws_hourly_images)
cli.add_command(aws_regions)
cli.add_command(azure_images)
cli.add_command(gcp_images)
