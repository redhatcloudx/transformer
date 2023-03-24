"""Tests for the Google transformer."""
import os

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
        ],
    )

    # Ensure directories are made.
    assert os.path.isdir(f"{tmp_path}/output/idx/list/sort-by-date")
    assert os.path.isdir(f"{tmp_path}/output/google/global")

    # Check list by date.
    with open(f"{tmp_path}/output/idx/list/sort-by-date/0") as fileh:
        assert "RHEL 7 X86_64" in fileh.read()

    # Check image data.
    with open(f"{tmp_path}/output/google/global/rhel_7_x86_64") as fileh:
        assert "RHEL 7 X86_64" in fileh.read()
