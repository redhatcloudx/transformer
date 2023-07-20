"""Test for the list os endpoint."""
import filecmp
import os

from cloudimagedirectory import transformer


def test_V2ListOS(runner, tmp_path):
    """Run transformer end to end and generate a list with all available
    operating systems."""
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
        f"{pwd}/tests/transformer/testdata/expected/v2/os/list",
        f"{tmp_path}/v2/os/list",
    )


def test_transformerV2ListOS(tmpdir):
    """Test list OS run method."""
    temporary_directory = tmpdir.mkdir("test")
    connection = transformer.connection.ConnectionFS(temporary_directory, [])
    runner = transformer.transform.TransformerV2ListOS(connection)
    chunk_size = 2
    runner.chunk_size = chunk_size
    data = [
        transformer.connection.DataEntry(
            "v1/azure/global/rh-ocp-worker_rh-ocp-worker_x64",
            {
                "date": "2019-01-01",
                "name": "test1",
                "arch": "arch1",
                "region": "region-1",
            },
        ),
        transformer.connection.DataEntry(
            "v1/google/global/rhel_9.0_sap_x86_64",
            {
                "date": "2020-01-01",
                "name": "test2",
                "arch": "arch2",
                "region": "region-1",
            },
        ),
        transformer.connection.DataEntry(
            "v1/aws/ap-northeast-2/rhel_8.5_hvm_arm64_hourly2",
            {
                "date": "2020-01-01",
                "name": "test2",
                "arch": "arch2",
                "region": "region-1",
            },
        ),
        transformer.connection.DataEntry(
            "v1/aws/some-region-1/unkown_distro",
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
        "v2/os/list",
        [
            {
                "name": "rhel",
                "display_name": "Red Hat Enterprise Linux",
                "description": "Red Hat Enterprise Linux",
                "count": 3,
            },
            {
                "name": "unkown",
                "display_name": "no display name",
                "description": "no description",
                "count": 1,
            },
        ],
    )

    assert expected.filename == results[0].filename
    assert expected.content == results[0].content
