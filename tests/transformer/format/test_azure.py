"""Test Azure image formatting."""
import re

import pytest
from cloudimagedirectory.format import format_azure

# Download the latest JSON file from Azure and run:
# jq '.[] | select(.publisher=="RedHat") | .version' eastus.json | sort | uniq | sort -R | head -n 25
AZURE_VERSION_STRINGS = [
    "8.2.2020050811",
    "7.4.2020071514",
    "8.2.20200509",
    "7.7.2020110301",
    "7.7.2020052922",
    "7.6.20190620",
    "8.0.2019050711",
    "8.6.2022103101",
    "8.1.20200901",
    "8.2.2021011801",
    "7.4.2020101118",
    "7.9.2020111302",
    "8.0.2022031402",
    "8.2.20200903",
    "7.5.2021051702",
    "311.170.20200224",
    "8.0.20210422",
    "8.1.20200821",
    "7.7.20191212",
    "8.0.20191023",
    "7.7.2020101117",
    "7.5.2019062018",
    "8.1.2020021915",
    "8.1.2020110712",
    "8.4.2021081003",
]

AZURE_IMAGE_RECORD = {
    "architecture": "x64",
    "offer": "rh-rhel",
    "publisher": "RedHat",
    "sku": "rh-rhel9-gen1",
    "urn": "RedHat:rh-rhel:rh-rhel9-gen1:9.2.2023070711",
    "version": "9.2.2023070711",
    "hyperVGeneration": "unknown",
}


@pytest.mark.parametrize("version_string", AZURE_VERSION_STRINGS)
def test_azure_version_string(version_string: str) -> None:
    """Test parsing a version string."""
    result = format_azure.parse_image_version_rhel(version_string)
    assert re.match(r"\d+\.\d+", result["version"])
    assert len(result["date"]) == 8


def test_azure_version_string_ugly() -> None:
    """Test parsing a bad version string from Azure."""
    version_string = "angry-hamster-4622"
    result = format_azure.parse_image_version_rhel(version_string)
    assert result == {}


@pytest.mark.parametrize("test_dates", ["20230131", "20233101"])
def test_date_conversion(test_dates: str) -> None:
    """Test date conversion."""
    result = format_azure.convert_date_rhel(test_dates)
    assert result == "2023-01-31"


def test_image_rhel() -> None:
    result = format_azure.image_rhel(AZURE_IMAGE_RECORD)
    assert result["name"] == "rh-rhel rh-rhel9-gen1 x64"
    assert result["arch"] == "x64"
    assert result["version"] == "9.2"
    assert result["imageId"] == "RedHat:rh-rhel:rh-rhel9-gen1:9.2.2023070711"
    assert result["date"] == "2023-07-07"
    assert result["virt"] == "unknown"
