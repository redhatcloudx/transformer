"""Tests for the Google transformer."""
import filecmp
import os

from cloudimagedirectory import transformer


def test_google_transformer_command(runner, tmp_path):
    """Verify that we can transform Google data."""
    result = runner.invoke(
        transformer.run,
        [
            "-f",
            "tests/transformer/testdata/input/raw/google/all.json",
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
    assert os.path.isdir(f"{tmp_path}/v1/google/global")

    # Get current directory
    pwd = os.getcwd()

    # Check image data by comparing the expected file and the output file byte by byte.
    assert filecmp.cmp(
        f"{pwd}/tests/transformer/testdata/expected/v1/google/global/rhel_7_x86_64",
        f"{tmp_path}/v1/google/global/rhel_7_x86_64",
    )
