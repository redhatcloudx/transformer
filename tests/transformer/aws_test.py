"""Tests for the AWS transformer."""
import os
import filecmp

from cloudimagedirectory import transformer


def test_aws_transformer_command(runner, tmp_path):
    """Verify that we can transform AWS data."""
    runner.invoke(
        transformer.run,
        [
            "-f",
            "tests/transformer/testdata/input/raw/aws/af-south-1.json",
            "-op=.",
            f"-dp={tmp_path}",
            "-v",
            "output",
            "--filter.until=none",
        ],
    )

    # Ensure the directory was made.
    assert os.path.isdir(f"{tmp_path}/output/aws/af-south-1")

    # Get current directory
    pwd = os.getcwd()

    # Check image data by comparing the expected file and the output file byte by byte.
    assert filecmp.cmp(f"{pwd}/tests/transformer/testdata/expected/aws/af-south-1/rhel_6.10_hvm_x86_64_hourly2",
                f"{tmp_path}/output/aws/af-south-1/rhel_6.10_hvm_x86_64_hourly2")
