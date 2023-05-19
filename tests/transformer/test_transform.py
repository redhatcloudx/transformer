"""Test basic transformations for the latest images."""
from cloudimagedirectory.connection import connection
from cloudimagedirectory.transform import transform


def test_transformeridxlistimagelatest():
    """Test basic transformations for the latest images."""
    runner = transform.TransformerIdxListImageLatest(connection.Connection())
    chunk_size = 2
    runner.chunk_size = chunk_size
    data = [
        connection.DataEntry(
            "aws/region-1/rhel-1",
            {
                "date": "2019-01-01",
                "name": "test1",
                "arch": "arch1",
                "region": "region-1",
            },
        ),
        connection.DataEntry(
            "raw/azure/region-1",
            {
                "date": "2020-01-01",
                "name": "invalid",
                "arch": "invalid",
            },
        ),
        connection.DataEntry(
            "azure/region-1/rhel-1",
            {
                "date": "2020-01-01",
                "name": "test2",
                "arch": "arch2",
                "region": "region-1",
            },
        ),
        connection.DataEntry(
            "google/region-1/rhel-1",
            {
                "date": "2022-01-01",
                "name": "test3",
                "arch": "arch3",
                "region": "region-1",
            },
        ),
        connection.DataEntry(
            "azure/region-1/rhel-1",
            {
                "date": "2015-01-01",
                "name": "test4",
                "arch": "arch4",
                "region": "region-1",
            },
        ),
    ]
    results = runner.run(data)
    expected_page1 = connection.DataEntry(
        "idx/list/sort-by-date/0",
        [
            {
                "date": "2022-01-01",
                "name": "test3",
                "arch": "arch3",
                "ref": "google/region-1/rhel-1",
                "provider": "google",
                "region": "region-1",
            },
            {
                "date": "2020-01-01",
                "name": "test2",
                "arch": "arch2",
                "ref": "azure/region-1/rhel-1",
                "provider": "azure",
                "region": "region-1",
            },
        ],
    )

    assert expected_page1.filename == results[0].filename
    assert expected_page1.content == results[0].content

    expected_page2 = connection.DataEntry(
        "idx/list/sort-by-date/1",
        [
            {
                "date": "2019-01-01",
                "name": "test1",
                "arch": "arch1",
                "ref": "aws/region-1/rhel-1",
                "provider": "aws",
                "region": "region-1",
            },
            {
                "date": "2015-01-01",
                "name": "test4",
                "arch": "arch4",
                "ref": "azure/region-1/rhel-1",
                "provider": "azure",
                "region": "region-1",
            },
        ],
    )

    assert expected_page2.filename == results[1].filename
    assert expected_page2.content == results[1].content

    # verify that only two pages exist
    assert 3 == len(results)
