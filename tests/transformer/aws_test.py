"""Tests for the AWS transformer."""
import filecmp
import os

from cloudimagedirectory import transformer


def test_aws_transformer_command(runner, tmp_path):
    """Verify that we can transform AWS data."""
    result = runner.invoke(
        transformer.run,
        [
            "-f",
            "tests/transformer/testdata/input/raw/aws/af-south-1.json",
            "-op=.",
            f"-dp={tmp_path}",
            "--filter.until=none",
        ],
    )

    assert result.exit_code == 0, f"expected no error, but got code {result.exit_code} and output:\n{result.output}"

    # Ensure the directory was made.
    assert os.path.isdir(f"{tmp_path}/v1/aws/af-south-1")

    # Get current directory
    pwd = os.getcwd()

    # Check image data by comparing the expected file and the output file byte by byte.
    assert filecmp.cmp(
        f"{pwd}/tests/transformer/testdata/expected/v1/aws/af-south-1/rhel_6.10_hvm_x86_64_hourly2",
        f"{tmp_path}/v1/aws/af-south-1/rhel_6.10_hvm_x86_64_hourly2",
    )
