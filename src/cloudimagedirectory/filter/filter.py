from typing import Callable


def FilterImageByFilename(word: str) -> Callable:
    """Filter images by filename."""

    print("filter images by filename: " + word)
    return lambda data: [
        d for d in data if not d.filename.lower().__contains__(word.lower())
    ]
