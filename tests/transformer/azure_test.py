"""Tests for the Azure transformer."""
import filecmp
import os

from cloudimagedirectory import transformer


def test_transformer_azure(runner, tmp_path):
    """Verify that we can transform Azure data."""
    result = runner.invoke(
        transformer.run,
        [
            "-f",
            "tests/transformer/testdata/input/raw/azure/eastus.json",
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

    # Ensure the directory was made.
    assert os.path.isdir(f"{tmp_path}/v1/azure/global")

    # Get current directory
    pwd = os.getcwd()

    # Check image data by comparing the expected file and the output file byte by byte.
    assert filecmp.cmp(
        f"{pwd}/tests/transformer/testdata/expected/v1/azure/global/osa_osa_311_x64",
        f"{tmp_path}/v1/azure/global/osa_osa_311_x64",
    )
