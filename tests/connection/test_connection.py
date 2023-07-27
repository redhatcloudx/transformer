"""Tests for the connection module."""
import os

import pytest
from cloudimagedirectory.connection.connection import ConnectionFS, DataEntry, OriginPathDoesNotExist


class TestDataEntry:
    """Tests for the DataEntry class."""

    def test_is_raw(self) -> None:
        """Verify that the raw format is detected."""
        temp = DataEntry("raw/foobar.json", None)
        assert temp.is_raw()

        temp = DataEntry("sooooonotrawhere", None)
        assert not temp.is_raw()

    def test_is_provided_by(self):
        """Verify that the origin is detected."""
        temp = DataEntry("foo/foobar.json", None)
        assert temp.is_provided_by("foo")

        temp = DataEntry("foobar.json", None)
        assert not temp.is_provided_by("foo")

    def test_is_API(self):
        """Verify that we can determine if this is an API entry."""
        # Plain v1 API.
        temp = DataEntry("v1/foobar.json", None)
        assert temp.is_API("v1")

        # Is a v1 api, but doesn't match our version spec.
        temp = DataEntry("v1/foobar.json", None)
        assert not temp.is_API("v2")

        # v2, but not enough slashes
        temp = DataEntry("v2/foobar.json", None)
        assert not temp.is_API("v2")

        # v2, enough slashes, but wrong hash length
        temp = DataEntry("v2/////////abcde/", None)
        assert not temp.is_API("v2")

        # v2, enough slashes, right hash length
        temp = DataEntry(f"v2/////////{'a'*40}/", None)
        assert not temp.is_API("v2")


class TestConnectionFS:
    """Tests for the connection module."""

    def test_without_origin_path(self) -> None:
        """Verify that a default origin path is used."""
        connection = ConnectionFS("", [])
        assert connection.origin_path == os.getcwd()

    def test_get_filenames_empty(self, tmpdir) -> None:
        """Verify that local files are used if no files are provided."""
        origin_path = tmpdir.mkdir("origin")
        origin_path.join("file1.json").write('{"foo": "bar"}')
        origin_path.join("file2.json").write('{"foo": "bar"}')

        result = ConnectionFS(origin_path, [])
        filenames = result.get_filenames()
        assert filenames[0].filename.endswith("file2.json")
        assert filenames[1].filename.endswith("file1.json")
        assert len(filenames) == 2

    def test_get_filenames_with_files(self, tmpdir) -> None:
        """Verify that local files are used when provided."""
        origin_path = tmpdir.mkdir("origin")
        origin_path.join("file1.json").write('{"foo": "bar"}')
        origin_path.join("file2.json").write('{"foo": "bar"}')

        result = ConnectionFS(origin_path, ["file1.json"])
        filenames = result.get_filenames()
        assert filenames[0].filename.endswith("file1.json")
        assert len(filenames) == 1

    def test_get_filenames_directory_missing(self) -> None:
        """Verify that an exception is raised if the directory is missing."""
        result = ConnectionFS("/foo/bar", [])
        with pytest.raises(OriginPathDoesNotExist):
            result.get_filenames()

    def test_get_content(self, tmpdir) -> None:
        """Verify an empty dict is returned when the file is empty."""
        origin_path = tmpdir.mkdir("origin")
        origin_path.join("file1.json").write("")

        result = ConnectionFS(origin_path, [origin_path.join("file1.json")])
        filenames = result.get_filenames()
        content = result.get_content(filenames[0])

        assert content.content == {}
