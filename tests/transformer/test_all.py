"""Tests for the All endpoint."""
import filecmp
import os

from cloudimagedirectory import transformer


def test_all(runner, tmp_path):
    """Run transformer end to end and generate a list with all image
    details."""
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

    if "0" != f"{result.exit_code}":
        assert (
            ""
            == f"expected no error, but got code: {result.exit_code} and output:"
            f" {result.output}"
        )

    # Get current directory
    pwd = os.getcwd()

    # Check image data by comparing the expected file and the output file byte by byte.
    assert filecmp.cmp(
        f"{pwd}/tests/transformer/testdata/expected/v2/all",
        f"{tmp_path}/v2/all",
    )
