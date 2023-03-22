import os


def test_transformer_google():
    assert 0 == os.system(
        "poetry run cloudimagedirectory-transformer -f"
        " ${PWD}/tests/transformer/testdata/input/google/all.json -op=${PWD} "
        " -dp=${PWD}/tests/transformer/testdata -v output"
    )
    assert 0 == os.system(
        "diff ${PWD}/tests/transformer/testdata/expected/google/global/rhel_7_x86_64"
        " ${PWD}/tests/transformer/testdata/output/google/global/rhel_7_x86_64"
    )
