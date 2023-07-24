"""Tests for the v2 Azure RHEL transformer."""
import filecmp
import os

from cloudimagedirectory import transformer


def test_aws_v2_rhel_transformer_command(runner, tmp_path):
    """Verify that we can transform Azure data for RHEL."""
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

    assert result.exit_code == 0, f"expected no error, but got code {result.exit_code} and output:\n{result.output}"

    # Ensure the directory was made.
    assert os.path.isdir(f"{tmp_path}/v2/os/rhel/provider/azure/version/311.161/region/global/image")

    # Get current directory
    pwd = os.getcwd()

    # Check image data by comparing the expected file and the output file byte by byte.
    assert filecmp.cmp(
        f"{pwd}/tests/transformer/testdata/expected/v2/os/rhel/provider/azure/version/311.161/region/global/image/93212c01392a1e372edd399bde5838066089b22c",
        f"{tmp_path}/v2/os/rhel/provider/azure/version/311.161/region/global/image/93212c01392a1e372edd399bde5838066089b22c",
    )
