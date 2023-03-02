import click
import sys

from cloudimagedirectory.s3 import s3
from cloudimagedirectory.transform import transform

@click.command()
@click.option('-id', '--origin.s3.aws.key-id', 'id', prompt='key-id', help='The key-id from your s3 bucket')
@click.option('-key', '--origin.s3.aws.access-key', 'access_key', prompt='Your authentication key', help='The authentication key for the s3 bucket')
@click.option('-op', '--origin.s3.path', 'origin_path', prompt='Origin s3 bucket path', help='The path to the source s3 bucket')
@click.option('-dp', '--destination.s3.path', 'destination_path', prompt='Destination s3 bucket path', help='The path to the destination s3 bucket')
@click.option('-b', '--origin.s3.bucket', 'bucket', prompt='Bucket name', help='The bucket name in the s3 bucket')
@click.option('-v', '--image.api.version', 'api', prompt='api-version', help='Image api version')
def run(id: str, access_key: int, origin_path: str, destination_path: str, bucket: str, api: str) -> None:
    """Connect to s3 bucket and format image data."""
    origin_connection = s3.ConnectionAWS(id, access_key, origin_path, bucket)
    try:
        print("connect to s3 bucket: " + bucket)
        origin_connection.connect()
    except:
        print("The connection to the s3 bucket didn't work")
    print("fetch filenames: " + bucket)
    files = origin_connection.get_filenames()
    
    pipeline = transform.Pipeline(origin_connection, [transform.TransformerAWS, transform.TransformerAZURE, transform.TransformerGOOGLE])
    print("run pipeline")
    results = pipeline.run(files)

    print("upload results")
    version_prefix = ""
    if api != "":
        version_prefix = api + "/"
    for result in results:
        result.filename = destination_path + "/" + version_prefix + result.filename
        print("put content to s3 bucket: " + bucket + " filename: " + result.filename)
        origin_connection.put_content(result)
