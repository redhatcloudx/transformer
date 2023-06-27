"""Tests for the cid2civ script."""
import os
import subprocess
import sys


def cid2civ(*args, in_file=None, out_file=None):
    """Run the cid2civ script and check its output."""
    pwd = os.getcwd()

    script = f"{pwd}/scripts/cid2civ"
    data = f"{pwd}/tests/scripts/testdata/cid2civ"
    website = f"{pwd}/tests/scripts/testdata/website"

    if in_file:
        args += (f"{data}/{in_file}",)

    if "download" in args:
        args += ("--website", f"file://{website}")

    result = subprocess.run(
        [script, "--verbose", *args], capture_output=True, text=True
    )

    print(result.stderr, file=sys.stderr)
    print(result.stdout, file=sys.stdout)
    result.check_returncode()

    if out_file:
        with open(f"{data}/{out_file}") as f:
            assert result.stdout.strip() == f.read().strip()

    return result


def test_cid2civ_help():
    """Test the --help option of the cid2civ script."""
    result = cid2civ("--help")
    assert "Usage:" in result.stdout
    assert "Commands:" in result.stdout
    assert "Arguments:" in result.stdout


def test_cid2civ_download():
    """Test the download command of the cid2civ script."""
    cid2civ("download", "aws", out_file="aws.cid")
    cid2civ("download", "azure", out_file="azure.cid")
    cid2civ("download", "google", out_file="google.cid")


def test_cid2civ_analyze():
    """Test the analyze command of the cid2civ script."""
    cid2civ("analyze", in_file="aws.cid", out_file="aws.txt")
    cid2civ("analyze", in_file="azure.cid", out_file="azure.txt")
    cid2civ("analyze", in_file="google.cid", out_file="google.txt")


def test_cid2civ_convert():
    """Test the convert command of the cid2civ script."""
    cid2civ("convert", in_file="aws.cid", out_file="aws.civ")
    cid2civ("convert", in_file="azure.cid", out_file="azure.civ")
    cid2civ("convert", in_file="google.cid", out_file="google.civ")
