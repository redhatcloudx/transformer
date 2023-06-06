"""Test for transforming images by date."""
import os


def test_list_images_by_date():
    """Run transformer end to end and generate a small list that contains image
    names."""

    assert 0 == os.system(
        "poetry run cloudimagedirectory-transformer -f "
        "${PWD}/tests/transformer/testdata/input/raw/azure/eastus.json,"
        "${PWD}/tests/transformer/testdata/input/raw/google/all.json,"
        "${PWD}/tests/transformer/testdata/input/raw/aws/af-south-1.json"
        " -op=${PWD} -dp=${PWD}/tests/transformer/testdata"
        " --filter.until=none"
    )
    assert 0 == os.system(
        "diff ${PWD}/tests/transformer/testdata/expected/v1/idx/list/sort-by-date/0"
        " ${PWD}/tests/transformer/testdata/v1/idx/list/sort-by-date/0"
    )
