"""Manage content in the S3 bucket."""
import json
import os
import pathlib
from pathlib import Path
from typing import Any


class OriginPathDoesNotExist(Exception):
    """Raise an exception if the origin path doesn't exist."""

    def __init__(self, origin_path: str):
        """Constructor for OriginPathDoesNotExist class."""
        super().__init__(f"The origin path '{origin_path}' doesn't exist.")


class DataEntry:
    """Handles a file from the bucket."""

    # TODO: Set Any to a specific type.
    def __init__(self, filename: str, content: Any) -> None:
        """Constructor for DataEntry class."""
        self.filename = filename
        self.content = content

    def is_raw(self) -> bool:
        """Check if the file is in raw format."""
        return "raw/" in self.filename

    def is_provided_by(self, name: str) -> bool:
        """Check the origin of the file."""
        return f"{name}/" in self.filename

    def is_API(self, api) -> bool:
        """Check if the file is the actual API entry and not a sub url."""
        path = self.filename.split("/")
        if path[0] != api:
            return False

        if path[0] == "v1":
            return True

        slash_count = self.filename.count("/")
        if slash_count != 10:
            return False

        # NOTE: check length of hash value.
        if len(path[len(path)-1]) != 40:
            return False

        return True


class ConnectionFS:
    """Handles the connection to the filesystem."""

    def __init__(self, origin_path: str, arg_files: list[str]):
        self.arg_files = arg_files
        self.origin_path = origin_path
        if self.origin_path == "":
            self.origin_path = os.getcwd()

    def get_filenames(self) -> list[DataEntry]:
        """Get the list of files in the bucket."""
        if len(self.arg_files) != 0:
            result = []
            for file in self.arg_files:
                result.append(DataEntry(file, None))
            return result
        return self.__list_files(self.origin_path)

    def __list_files(self, directory: str) -> list[DataEntry]:
        data_files = []
        p = pathlib.Path(directory)
        if p.exists():
            for child in p.glob("**/*.json"):
                data_files.append(DataEntry(str(child.resolve()), None))
        else:
            raise OriginPathDoesNotExist(directory)
        return data_files

    def get_content(self, data: DataEntry) -> DataEntry:
        """Get the content of a file in the bucket."""
        content: str = ""
        content = Path(data.filename).read_text()
        if content == "":
            content = "{}"
        content = json.loads(content)
        return DataEntry(data.filename, content)

    def put_content(self, data: DataEntry) -> None:
        """Put the content of a file in the bucket."""
        json_data = json.dumps(data.content)
        tmp = data.filename.split("/")
        tmp = tmp[: len(tmp) - 1]
        directory_path = "/".join(tmp)
        os.makedirs(directory_path, exist_ok=True)
        Path(data.filename).write_text(json_data + "\n")
