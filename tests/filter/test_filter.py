"""Tests for filters."""
import pandas as pd
from cloudimagedirectory.connection import connection
from cloudimagedirectory.filter import filter


def test_filterImageByLatestUpdate():
    """Test for filtering the images from a given date."""
    data = [
        connection.DataEntry(
            "aws/region-1/rhel-1",
            None,
        ),
        connection.DataEntry(
            "azure/region-1/rhel-1",
            {
                "date": "2026-01-01",
            },
        ),
        connection.DataEntry(
            "azure/region-1/rhel-1",
            {
                "date": "1920-01-01",
            },
        ),
        connection.DataEntry(
            "google/region-1/rhel-1",
            {
                "date": "2024-01-01",
            },
        ),
    ]
    results = filter.FilterImageByLatestUpdate(pd.to_datetime("2023-04-04"))(data)
    expected = [
        connection.DataEntry(
            "azure/region-1/rhel-1",
            {
                "date": "2026-01-01",
            },
        ),
        connection.DataEntry(
            "google/region-1/rhel-1",
            {
                "date": "2024-01-01",
            },
        ),
    ]

    for r in results:
        print(r.content)

    assert len(expected) == len(results)
    assert expected[0].content == results[0].content
    assert expected[1].content == results[1].content


def test_FilterImageByUniqueName():
    """Test for filtering latest images with unique names."""
    data = [
        # Region 1
        connection.DataEntry(
            "aws/region-1/rhel-1",
            None,
        ),
        connection.DataEntry(
            "azure/region-1/rhel-3",
            {
                "name": "rhel-3",
                "date": "2023-01-01",
                "region": "region-1",
            },
        ),
        connection.DataEntry(
            "azure/region-1/rhel-1",
            {
                "name": "rhel-1",
                "date": "2020-01-01",
                "region": "region-1",
            },
        ),
        connection.DataEntry(
            "azure/region-1/rhel-2",
            {
                "name": "rhel-2",
                "date": "2022-01-01",
                "region": "region-1",
            },
        ),
        connection.DataEntry(
            "azure/region-1/rhel-3",
            {
                "name": "rhel-3",
                "date": "2022-01-01",
                "region": "region-1",
            },
        ),
        connection.DataEntry(
            "azure/region-1/rhel-3",
            {
                "name": "rhel-3",
                "date": "2020-01-01",
                "region": "region-1",
            },
        ),
        connection.DataEntry(
            "google/region-1/rhel-1",
            {
                "name": "rhel-1",
                "date": "2024-01-01",
                "region": "region-1",
            },
        ),
        # Region 2
        connection.DataEntry(
            "aws/region-2/rhel-1",
            None,
        ),
        connection.DataEntry(
            "azure/region-2/rhel-3",
            {
                "name": "rhel-3",
                "date": "2023-01-01",
                "region": "region-2",
            },
        ),
        connection.DataEntry(
            "azure/region-2/rhel-1",
            {
                "name": "rhel-1",
                "date": "2020-01-01",
                "region": "region-2",
            },
        ),
        connection.DataEntry(
            "azure/region-2/rhel-2",
            {
                "name": "rhel-2",
                "date": "2022-01-01",
                "region": "region-2",
            },
        ),
        connection.DataEntry(
            "azure/region-2/rhel-3",
            {
                "name": "rhel-3",
                "date": "2022-01-01",
                "region": "region-2",
            },
        ),
        connection.DataEntry(
            "azure/region-2/rhel-3",
            {
                "name": "rhel-3",
                "date": "2020-01-01",
                "region": "region-2",
            },
        ),
        connection.DataEntry(
            "google/region-2/rhel-1",
            {
                "name": "rhel-1",
                "date": "2024-01-01",
                "region": "region-2",
            },
        ),
    ]
    results = filter.FilterImageByUniqueName()(data)
    expected = [
        connection.DataEntry(
            "azure/region-1/rhel-3",
            {
                "name": "rhel-3",
                "date": "2023-01-01",
                "region": "region-1",
            },
        ),
        connection.DataEntry(
            "azure/region-1/rhel-2",
            {
                "name": "rhel-2",
                "date": "2022-01-01",
                "region": "region-1",
            },
        ),
        connection.DataEntry(
            "google/region-1/rhel-1",
            {
                "name": "rhel-1",
                "date": "2024-01-01",
                "region": "region-1",
            },
        ),
        connection.DataEntry(
            "azure/region-2/rhel-3",
            {
                "name": "rhel-3",
                "date": "2023-01-01",
                "region": "region-2",
            },
        ),
        connection.DataEntry(
            "azure/region-2/rhel-2",
            {
                "name": "rhel-2",
                "date": "2022-01-01",
                "region": "region-2",
            },
        ),
        connection.DataEntry(
            "google/region-2/rhel-1",
            {
                "name": "rhel-1",
                "date": "2024-01-01",
                "region": "region-2",
            },
        ),
    ]

    for r in results:
        print(r.content)

    assert len(expected) == len(results)
    assert expected[0].content == results[0].content
    assert expected[1].content == results[1].content
    assert expected[2].content == results[2].content
    assert expected[3].content == results[3].content
    assert expected[4].content == results[4].content
    assert expected[5].content == results[5].content
