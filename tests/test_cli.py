"""Update images from public cloud APIs."""
from __future__ import annotations

import json

import click.testing
import pytest

from rhelocator import cli
from rhelocator import config


@pytest.fixture
def runner():
    return click.testing.CliRunner()


@pytest.mark.e2e
def test_aws_hourly_images_live(runner):
    """Run a live test against the AWS API to get hourly images via CLI."""
    result = runner.invoke(cli.aws_hourly_images, ["--region=us-east-1"])
    parsed = json.loads(result.output)

    # Ensure we only received hourly images with the proper billing code.
    assert {x["UsageOperation"] for x in parsed} == {config.AWS_HOURLY_BILLING_CODE}
    assert result.exit_code == 0


def test_aws_hourly_images_offline(runner, mock_aws_regions, mock_aws_images):
    """Run an offline test against the AWS API to get hourly images via CLI."""
    result = runner.invoke(cli.aws_hourly_images, ["--region=us-east-1"])
    parsed = json.loads(result.output)

    # Ensure we only received hourly images with the proper billing code.
    assert {x["UsageOperation"] for x in parsed} == {config.AWS_HOURLY_BILLING_CODE}
    assert result.exit_code == 0


def test_aws_hourly_images_missing_region(runner):
    """Simulate a failure to provide a region for the hourly images command."""
    result = runner.invoke(cli.aws_hourly_images)

    assert "Provide a valid AWS region" in result.output
    assert result.exit_code == 2


def test_aws_hourly_images_invalid_region(mock_aws_regions, runner):
    """Simulate a failure to provide a valid region for the hourly images command."""
    result = runner.invoke(cli.aws_hourly_images, ["--region=antarctica-west-99"])

    assert "antarctica-west-99 is not valid" in result.output
    assert result.exit_code == 2


@pytest.mark.e2e
def test_aws_regions_live(runner):
    """Run a live test against the AWS API to get hourly images via CLI."""
    result = runner.invoke(cli.aws_regions)
    parsed = json.loads(result.output)

    assert isinstance(parsed, list)
    assert "us-east-1" in parsed
    assert result.exit_code == 0


def test_aws_regions_offline(mock_aws_regions, runner):
    """Run an offline test against the AWS API to get hourly images via CLI."""
    result = runner.invoke(cli.aws_regions)

    parsed = json.loads(result.output)

    assert isinstance(parsed, list)
    assert "us-east-1" in parsed
    assert result.exit_code == 0
