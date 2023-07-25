"""Tests for the v2 Google RHEL transformer."""
import filecmp
import os

from cloudimagedirectory import transformer


def test_aws_v2_rhel_transformer_command(runner, tmp_path):
    """Verify that we can transform Google data for RHEL."""
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

    assert result.exit_code == 0, f"expected no error, but got code {result.exit_code} and output:\n{result.output}"

    # Ensure the directory was made.
    assert os.path.isdir(f"{tmp_path}/v2/os/rhel/provider/google/version/7/region/global/image")

    # Get current directory
    pwd = os.getcwd()

    # Check image data by comparing the expected file and the output file byte by byte.
    assert filecmp.cmp(
        f"{pwd}/tests/transformer/testdata/expected/v2/os/rhel/provider/google/version/7/region/global/image/a2f9b1c21e096445099c419aa0c0c9bc32657059",
        f"{tmp_path}/v2/os/rhel/provider/google/version/7/region/global/image/a2f9b1c21e096445099c419aa0c0c9bc32657059",
    )
