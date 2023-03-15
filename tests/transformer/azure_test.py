import os

def test_transformer_azure():
    assert 0 == os.system('poetry run cloudimagedirectory-transformer -f ${PWD}/tests/transformer/testdata/input/azure/eastus.json -op=${PWD}  -dp=${PWD}/tests/transformer/testdata -v output')
    assert 0 == os.system('diff ${PWD}/tests/transformer/testdata/expected/azure/eastus/osa_osa_311_x64 ${PWD}/tests/transformer/testdata/output/azure/eastus/osa_osa_311_x64')
