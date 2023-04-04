from typing import Callable

import pandas as pd
import pytz # type: ignore


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
        if d.content is not None
        and pd.Timestamp(d.content["date"]).replace(tzinfo=pytz.UTC) > latestDate
    ]
