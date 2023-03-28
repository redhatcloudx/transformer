from cloudimagedirectory.connection import connection
from cloudimagedirectory.transform import transform


def test_transformeridxlistimagelatest():
    runner = transform.TransformerIdxListImageLatest(connection.Connection())
    chunk_size = 2
    runner.chunk_size = chunk_size
    data = [
        connection.DataEntry(
            "images/aws/region-1",
            {
                "date": "2019-01-01",
                "name": "test1",
                "arch": "arch1",
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
            "images/azure/region-1",
            {
                "date": "2020-01-01",
                "name": "test2",
                "arch": "arch2",
            },
        ),
        connection.DataEntry(
            "images/google/region-1",
            {
                "date": "2022-01-01",
                "name": "test3",
                "arch": "arch3",
            },
        ),
        connection.DataEntry(
            "images/azure/region-1",
            {
                "date": "2015-01-01",
                "name": "test4",
                "arch": "arch4",
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
                "ref": "images/google/region-1",
                "provider": "google",
            },
            {
                "date": "2020-01-01",
                "name": "test2",
                "arch": "arch2",
                "ref": "images/azure/region-1",
                "provider": "azure",
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
                "ref": "images/aws/region-1",
                "provider": "aws",
            },
            {
                "date": "2015-01-01",
                "name": "test4",
                "arch": "arch4",
                "ref": "images/azure/region-1",
                "provider": "azure",
            },
        ],
    )

    assert expected_page2.filename == results[1].filename
    assert expected_page2.content == results[1].content

    # verify that only two pages exist
    assert 2 == len(results)
