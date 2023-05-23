"""Tests for the Google transformer."""
import os
import filecmp

from cloudimagedirectory import transformer


def test_google_transformer_command(runner, tmp_path):
    """Verify that we can transform Google data."""
    runner.invoke(
        transformer.run,
        [
            "-f",
            "tests/transformer/testdata/input/raw/google/all.json",
            "-op=.",
            f"-dp={tmp_path}",
            "-v",
            "output",
            "--filter.until=none",
        ],
    )

    # Ensure the directory was made.
    assert os.path.isdir(f"{tmp_path}/output/google/global")

    # Get current directory
    pwd = os.getcwd()

    # Check image data by comparing the expected file and the output file byte by byte.
    assert filecmp.cmp(f"{pwd}/tests/transformer/testdata/expected/google/global/rhel_7_x86_64",
                f"{tmp_path}/output/google/global/rhel_7_x86_64")
