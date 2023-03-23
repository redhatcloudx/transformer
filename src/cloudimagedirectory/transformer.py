import click

from cloudimagedirectory.connection import connection
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
    "-v", "--image.api.version", "api", prompt="api-version", help="Image api version"
)
@click.option(
    "-f",
    "--input.files",
    "arg_files",
    default="none",
    prompt="files to process",
    help="List of predefined files to process",
)
def run(origin_path: str, destination_path: str, api: str, arg_files: str) -> None:
    """Get content from filesystem format image data."""
    target: list[str] = []
    if arg_files != "none":
        target = arg_files.split(",")
    origin_connection = connection.ConnectionFS(origin_path, target)
    filenames = origin_connection.get_filenames()
    for file in filenames:
        print("input: " + file.filename)

    pipeline = transform.Pipeline(
        origin_connection,
        [
            transform.TransformerAWS,
            transform.TransformerAZURE,
            transform.TransformerGOOGLE,
        ],
    )
    print("run pipeline")
    results = pipeline.run(filenames)

    version_prefix = ""
    if api != "":
        version_prefix = api + "/"
    for result in results:
        result.filename = destination_path + "/" + version_prefix + result.filename
        if not result.is_raw():
            origin_connection.put_content(result)
