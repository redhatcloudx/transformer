import click
import sys

from cloudimagedirectory.connection import connection
from cloudimagedirectory.transform import transform

@click.command()
@click.option('-op', '--origin.path', 'origin_path', prompt='Origin bucket path', help='The path to the source s3 bucket')
@click.option('-dp', '--destination.path', 'destination_path', prompt='Destination bucket path', help='The path to the destination s3 bucket')
@click.option('-v', '--image.api.version', 'api', prompt='api-version', help='Image api version')
@click.option('-f', '--input.files', 'arg_files', default="None", prompt='files to process', help='List of predefined files to process')
def run(origin_path: str, destination_path: str, api: str, arg_files: str) -> None:
    """Get conentent from filesystem format image data."""
    target = []
    if arg_files != "None":
        target = arg_files.split(",")
    origin_connection = connection.ConnectionFS(origin_path, target)
    origin_connection.put_content(connection.DataEntry("test.txt", "hallo-welt"))
    data = origin_connection.get_content(connection.DataEntry("test.txt", ""))
    print(data.content)
    filenames = origin_connection.get_filenames()
    for file in filenames:
        print(file.filename)
    
    pipeline = transform.Pipeline(origin_connection, [transform.TransformerAWS, transform.TransformerAZURE, transform.TransformerGOOGLE])
    print("run pipeline")
    results = pipeline.run(filenames)

    print("upload results")
    version_prefix = ""
    if api != "":
        version_prefix = api + "/"
    for result in results:
        result.filename = destination_path + "/" + version_prefix + result.filename
        print("put content to filesystem. filename: " + result.filename)
        #origin_connection.put_content(result)
