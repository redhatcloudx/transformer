"""Test for the list version endpoint."""
import filecmp
import os

from cloudimagedirectory import transformer


def test_V2ListVersion(runner, tmp_path):
    """Run transformer end to end and generate a list with all available
    versions for the specific provider."""
    result = runner.invoke(
        transformer.run,
        [
            "-f",
            "tests/transformer/testdata/input/raw/google/all.json,tests/transformer/testdata/input/raw/aws/af-south-1.json,tests/transformer/testdata/input/raw/azure/eastus.json",
            "-op=.",
            f"-dp={tmp_path}",
            "--filter.until=none",
        ],
    )

    assert result.exit_code == 0, f"expected no error, but got code {result.exit_code} and output:\n{result.output}"

    # Get current directory
    pwd = os.getcwd()

    # Check image data by comparing the expected file and the output file byte by byte.
    assert filecmp.cmp(
        f"{pwd}/tests/transformer/testdata/expected/v2/os/rhel/provider/google/version/list",
        f"{tmp_path}/v2/os/rhel/provider/google/version/list",
    )


def test_transformerV2ListVersion(tmpdir):
    """Test list version run method."""
    temporary_directory = tmpdir.mkdir("test")
    connection = transformer.connection.ConnectionFS(temporary_directory, [])
    runner = transformer.transform.TransformerV2ListVersionByProvider(connection)
    chunk_size = 2
    runner.chunk_size = chunk_size
    data = [
        transformer.connection.DataEntry(
            "v2/os/rhel/provider/google/version/9/region/global/image/9054fbe0b622c638224d50d20824d2ff6782e308",
            {
                "date": "2023-03-06T12:57:17.827-08:00",
                "name": "test2",
                "arch": "ARM64",
                "region": "global",
            },
        ),
        transformer.connection.DataEntry(
            "v2/os/rhel/provider/google/version/8/region/global/image/dba7673010f19a94af4345453005933fd511bea9",
            {
                "date": "2019-01-01",
                "name": "test1",
                "arch": "arch1",
                "region": "global",
            },
        ),
        transformer.connection.DataEntry(
            "v2/os/rhel/provider/aws/version/8/region/ap-south-2/image/9054fbe0b622c638224d50d20824d2ff6782e308",
            {
                "date": "2020-01-01",
                "name": "test2",
                "arch": "arch2",
                "region": "ap-south-2",
            },
        ),
        transformer.connection.DataEntry(
            "v2/os/unkown/provider/aws/version/7/region/some-region-1/image/9054fbe0b622c638224d50d20824d2ff6782e308",
            {
                "date": "2020-01-01",
                "name": "test2",
                "arch": "arch2",
                "region": "region-1",
            },
        ),
    ]
    results = runner.run(data)
    expected = transformer.connection.DataEntry(
        "v2/os/rhel/provider/google/version/list",
        {"8": 1, "9": 1},
    )

    assert expected.filename == results[0].filename
    assert expected.content == results[0].content
