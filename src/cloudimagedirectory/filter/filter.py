from typing import Callable

import pandas as pd
import pytz  # type: ignore


def get_utc_datetime(date_string):
    """Get a timezone-aware comparable UTC datetime object.

    Returns: A datetime object representing the date string.
    """
    return pd.Timestamp(date_string).replace(tzinfo=pytz.UTC)


def FilterImageByFilename(word: str) -> Callable:
    """Filter images by filename."""
    print("filter images by filename: " + word)
    return lambda data: [
        d for d in data if not d.filename.lower().__contains__(word.lower())
    ]


def FilterImageByLatestUpdate(latestDate: pd.Timestamp) -> Callable:
    """Filter images by latest date."""
    print(f"filter images by latest date: {latestDate}")
    latestDate = latestDate.replace(tzinfo=pytz.UTC)

    return lambda data: [
        d
        for d in data
        if d.content is not None and get_utc_datetime(d.content["date"]) > latestDate
    ]


def FilterImageByUniqueReference() -> Callable:
    """Filter latest images with unique references."""
    print("filter images by unique references")
    return _filter_by_unique_references


def _filter_by_unique_references(data):
    """Return a list of latest images with unique references."""
    # Create a dictionary of image references and latest data entries.
    # The dictionary ensures uniqueness of the references and preserves
    # insertion order of the data entries.
    unique_data = {}

    for entry in data:
        # Skip data entries without content.
        if entry.content is None:
            continue

        # Compare the data entry with the last inserted entry with
        # the same reference. If the new entry is older, do nothing.
        ref = entry.filename
        date = entry.content["date"]

        if ref in unique_data:
            latest_entry = unique_data[ref]
            latest_date = latest_entry.content["date"]

            if get_utc_datetime(latest_date) > get_utc_datetime(date):
                continue

        # Add a new latest data entry for this image reference.
        # Reinsert the key to preserve the insertion order.
        unique_data.pop(ref, None)
        unique_data[ref] = entry

    # Return a list of latest entries with unique image references.
    return list(unique_data.values())
