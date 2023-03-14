import os

def test_transformer_aws():
    assert 0 == os.system('poetry run cloudimagedirectory-transformer -f ${PWD}/tests/transformer/testdata/input/aws-af-south-1.json -op=${PWD}  -dp=${PWD}/tests/transformer/testdata -v output')
    assert 0 == os.system('diff ${PWD}/tests/transformer/testdata/expected/aws/af-south-1/rhel_6.10_hvm_x86_64_hourly2 ${PWD}/tests/transformer/testdata/output/aws/aws-af-south-1/rhel_6.10_hvm_x86_64_hourly2')
    
