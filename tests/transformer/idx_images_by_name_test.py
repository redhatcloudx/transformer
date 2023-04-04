import os


def test_list_names_of_images():
    """Run transformer end to end and generate a small list that contains image names."""

    assert 0 == os.system(
        "poetry run cloudimagedirectory-transformer -f "
        "${PWD}/tests/transformer/testdata/input/raw/azure/eastus.json,"
        "${PWD}/tests/transformer/testdata/input/raw/google/all.json,"
        "${PWD}/tests/transformer/testdata/input/raw/aws/af-south-1.json"
        " -op=${PWD} -dp=${PWD}/tests/transformer/testdata -v output"
        " --filter.until=none"
    )
    assert 0 == os.system(
        "diff ${PWD}/tests/transformer/testdata/expected/idx/list/image-names"
        " ${PWD}/tests/transformer/testdata/output/idx/list/image-names"
    )
