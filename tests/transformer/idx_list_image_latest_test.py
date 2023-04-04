import os


def test_transformer_idx_list_image_latest():
    """Run transformer end to end with Azure input data."""
    assert 0 == os.system(
        "poetry run cloudimagedirectory-transformer -f "
        "${PWD}/tests/transformer/testdata/input/raw/azure/eastus.json,"
        "${PWD}/tests/transformer/testdata/input/raw/google/all.json,"
        "${PWD}/tests/transformer/testdata/input/raw/aws/af-south-1.json"
        " -op=${PWD} -dp=${PWD}/tests/transformer/testdata -v output"
        " --filter.until=none"
    )
    assert 0 == os.system(
        "diff ${PWD}/tests/transformer/testdata/expected/idx/list/sort-by-date/0"
        " ${PWD}/tests/transformer/testdata/output/idx/list/sort-by-date/0"
    )

    assert 0 == os.system(
        "diff ${PWD}/tests/transformer/testdata/expected/idx/list/sort-by-date-aws/0"
        " ${PWD}/tests/transformer/testdata/output/idx/list/sort-by-date-aws/0"
    )

    assert 0 == os.system(
        "diff ${PWD}/tests/transformer/testdata/expected/idx/list/sort-by-date-google/0"
        " ${PWD}/tests/transformer/testdata/output/idx/list/sort-by-date-google/0"
    )

    assert 0 == os.system(
        "diff ${PWD}/tests/transformer/testdata/expected/idx/list/sort-by-date-azure/0"
        " ${PWD}/tests/transformer/testdata/output/idx/list/sort-by-date-azure/0"
    )

    assert 0 == os.system(
        "diff ${PWD}/tests/transformer/testdata/expected/idx/list/sort-by-date/pages"
        " ${PWD}/tests/transformer/testdata/output/idx/list/sort-by-date/pages"
    )

    assert 0 == os.system(
        "diff ${PWD}/tests/transformer/testdata/expected/idx/list/sort-by-date-aws/pages"
        " ${PWD}/tests/transformer/testdata/output/idx/list/sort-by-date-aws/pages"
    )

    assert 0 == os.system(
        "diff ${PWD}/tests/transformer/testdata/expected/idx/list/sort-by-date-azure/pages"
        " ${PWD}/tests/transformer/testdata/output/idx/list/sort-by-date-azure/pages"
    )

    assert 0 == os.system(
        "diff ${PWD}/tests/transformer/testdata/expected/idx/list/sort-by-date-google/pages"
        " ${PWD}/tests/transformer/testdata/output/idx/list/sort-by-date-google/pages"
    )
