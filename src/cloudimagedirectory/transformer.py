"""Add command for transforming image data."""
import datetime

import click
import pandas as pd

from cloudimagedirectory.connection import connection
from cloudimagedirectory.filter import filter
from cloudimagedirectory.transform import transform


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
def run(
    origin_path: str, destination_path: str, arg_files: str, filter_until: str
) -> None:
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
        filter.FilterImageByUniqueName(),
    ]

    if filter_until == "default":
        # NOTE: Subtract 2 years from current time
        filter_after = datetime.datetime.now() - datetime.timedelta(days=2 * 365)
        filters.append(filter.FilterImageByLatestUpdate(filter_after))
    elif filter_until != "" and filter_until != "none":
        filter_after = pd.to_datetime(filter_until)
        filters.append(filter.FilterImageByLatestUpdate(filter_after))

    pipeline = transform.Pipeline(
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
            transform.TransformerV2All,
        ],
    )
    print("run pipeline")
    results = pipeline.run(filenames)

    for result in results:
        result.filename = destination_path + "/" + result.filename
        if not result.is_raw():
            origin_connection.put_content(result)
