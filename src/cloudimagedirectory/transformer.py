"""Add command for transforming image data."""
import datetime

import click
import pandas as pd

from cloudimagedirectory.connection import connection
from cloudimagedirectory.filter import filter
from cloudimagedirectory.transform import transform

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider

@click.command()
@click.option(
    "-op",
    "--origin.path",
    "origin_path",
    prompt="Origin filesystem path",
    help="The path to the filesystem source",
)
@click.option(
    "-dp",
    "--destination.path",
    "destination_path",
    prompt="Destination filesystem path",
    help="The path to the filesystem destination",
)
@click.option(
    "-fu",
    "--filter.until",
    "filter_until",
    prompt="Ignore all images after timestamp e.g. (YYYY-MM-DD)",
    default="none",
    help="Ignores all images after given timestamp",
)
@click.option(
    "-f",
    "--input.files",
    "arg_files",
    default="none",
    prompt="files to process",
    help="List of predefined files to process",
)
def run(origin_path: str, destination_path: str, arg_files: str, filter_until: str) -> None:
    # metrics.get_meter_provider().start_pipeline(ConsoleMetricExporter(), interval=5)

    """Get content from filesystem format image data."""
    target: list[str] = []
    if arg_files != "none":
        target = arg_files.split(",")
    origin_connection = connection.ConnectionFS(origin_path, target)
    filenames = origin_connection.get_filenames()
    for file in filenames:
        print("input: " + file.filename)

    filters = [
        filter.FilterImageByFilename("test"),
        filter.FilterImageByFilename("beta"),
        filter.FilterImageByFilename("raw"),
        filter.FilterImageByUniqueName(),
    ]

    if filter_until == "default":
        # NOTE: Subtract 2 years from current time
        filter_after = datetime.datetime.now() - datetime.timedelta(days=2 * 365)
        filters.append(filter.FilterImageByLatestUpdate(filter_after))
    elif filter_until != "" and filter_until != "none":
        filter_after = pd.to_datetime(filter_until)
        filters.append(filter.FilterImageByLatestUpdate(filter_after))

    pipeline_v1 = transform.Pipeline(
        origin_connection,
        [
            transform.TransformerAWS,
            transform.TransformerAZURE,
            transform.TransformerGoogle,
        ],
        filters,
        [
            transform.TransformerIdxListImageNames,
            transform.TransformerIdxListImageLatest,
            transform.TransformerIdxListImageLatestGoogle,
            transform.TransformerIdxListImageLatestAWS,
            transform.TransformerIdxListImageLatestAZURE,
        ],
    )
    print("run pipeline v1")
    results = pipeline_v1.run(filenames)

    # NOTE: Introducing a second pipeline, to avoid filtering of v1/v2 data
    # based on the image filename.
    # We do not adapt the filter, since v1 will be removed soon.
    pipeline_v2 = transform.Pipeline(
        origin_connection,
        [
            transform.TransformerAWSV2RHEL,
            transform.TransformerAzureV2RHEL,
            transform.TransformerGoogleV2RHEL,
        ],
        filters,
        [
            transform.TransformerV2All,
            transform.TransformerV2ListOS,
            transform.TransformerV2ListProviderByOS,
            transform.TransformerV2ListVersionByProvider,
            transform.TransformerV2ListRegionByVersion,
            transform.TransformerV2ListImageByRegion,
        ],
    )
    print("run pipeline v2")
    results.extend(pipeline_v2.run(filenames))

    for result in results:
        result.filename = destination_path + "/" + result.filename
        if not result.is_raw():
            origin_connection.put_content(result)
