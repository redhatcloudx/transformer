from typing import Any, Callable

import pandas as pd
import pytz
from cloudimagedirectory.connection.connection import DataEntry
from opentelemetry import metrics

meter = metrics.get_meter("transformer.pipeline.filter.meter")


def get_utc_datetime(date_string: str) -> pd.Timestamp:  # type: ignore[no-any-unimported]
    """Get a timezone-aware comparable UTC datetime object.

    Returns: A datetime object representing the date string.
    """
    return pd.Timestamp(date_string).replace(tzinfo=pytz.UTC)


filtered_image_by_filename_counter = meter.create_counter(
    name="filter.image.by_filename.count",
    description="Counts the number of filtered images by filename",
    unit="1",
)


def FilterImageByFilename(word: str) -> Callable:
    """Filter images by filename."""
    print("filter images by filename: " + word)

    def _filter_image_by_filename(data: list[DataEntry]) -> list:
        result = []
        for d in data:
            if not d.filename.lower().__contains__(word.lower()):
                result.append(d)
            else:
                filtered_image_by_filename_counter.add(1, {"word": word})
        return result

    return _filter_image_by_filename


filtered_image_by_latest_update_counter = meter.create_counter(
    name="filter.image.by_latest_update.count",
    description="Counts the number of filtered images by latest update",
    unit="1",
)


def FilterImageByLatestUpdate(latestDate: pd.Timestamp) -> Callable:  # type: ignore[no-any-unimported]
    """Filter images by latest date."""
    print(f"filter images by latest date: {latestDate}")
    latestDate = latestDate.replace(tzinfo=pytz.UTC)

    def _filter_image_by_latest_update(data: list) -> list:
        result = []
        for d in data:
            if d.content is not None and get_utc_datetime(d.content["date"]) > latestDate:
                result.append(d)
            else:
                filtered_image_by_latest_update_counter.add(1, {"latest_date": latestDate.strftime("%m/%d/%Y")})
        return result

    return _filter_image_by_latest_update


def FilterImageByUniqueName() -> Callable:
    """Filter latest images with unique names."""
    print("filter images by unique names")
    return _filter_by_unique_names


filtered_image_by_unique_names_counter = meter.create_counter(
    name="filter.image.by_unique_name.counter",
    description="Counts the number of filtered images by unique names",
    unit="1",
)


def _filter_by_unique_names(data: list) -> list:
    """Return a list of latest images with unique names."""
    # Create a dictionary of image names and latest data entries.
    # The dictionary ensures uniqueness of the names and preserves
    # insertion order of the data entries.
    unique_data: dict[Any, Any] = {}

    for entry in data:
        # Skip data entries without content.
        if entry.content is None:
            continue

        # Compare the data entry with the last inserted entry of
        # the same name. If the new entry is older, do nothing.
        name_raw = entry.content["name"]
        if "region" in entry.content:
            region = entry.content["region"].replace("-", "_")
            name = f"{name_raw}_{region}"
        else:
            name = name_raw
        date = entry.content["date"]

        if name in unique_data:
            latest_entry = unique_data[name]
            latest_date = latest_entry.content["date"]

            if get_utc_datetime(latest_date) > get_utc_datetime(date):
                continue

        # Add a new latest data entry for this image name.
        # Reinsert the key to preserve the insertion order.
        unique_data.pop(name, None)
        unique_data[name] = entry

    # Return a list of latest entries with unique image names.
    result = list(unique_data.values())
    filtered_image_by_unique_names_counter.add(len(data) - len(result))
    return result
