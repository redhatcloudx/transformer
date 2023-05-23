"""Tests for the Azure transformer."""
import os
import filecmp

from cloudimagedirectory import transformer

def test_transformer_azure(runner, tmp_path):
    """Verify that we can transform Azure data."""
    runner.invoke(
        transformer.run,
        [
            "-f",
            "tests/transformer/testdata/input/raw/azure/eastus.json",
            "-op=.",
            f"-dp={tmp_path}",
            "-v",
            "output",
            "--filter.until=none",
        ],
    )

    # Ensure the directory was made.
    assert os.path.isdir(f"{tmp_path}/output/azure/eastus")

    # Get current directory
    pwd = os.getcwd()

    # Check image data by comparing the expected file and the output file byte by byte.
    assert filecmp.cmp(f"{pwd}/tests/transformer/testdata/expected/azure/eastus/osa_osa_311_x64",
                f"{tmp_path}/output/azure/eastus/osa_osa_311_x64")
