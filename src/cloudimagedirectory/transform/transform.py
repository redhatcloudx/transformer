"""Transforms the raw data into useful data."""
import os

from typing import Callable

from cloudimagedirectory import config
from cloudimagedirectory.connection import connection
from cloudimagedirectory.update_images import aws
from cloudimagedirectory.update_images import azure
from cloudimagedirectory.update_images import google


class Pipeline:
    """Builds a pipeline of transformer tasks."""

    transformers: list[Callable] = []

    def __init__(self, src_conn, transformer_funcs: list[Callable]):
        """Initialize the pipeline."""
        self.src_conn = src_conn
        for transformer_func in transformer_funcs:
            self.transformers.append(transformer_func(self.src_conn))

    def run(self, data):
        """Run the pipeline."""
        results = data
        for transformer in self.transformers:
            results.extend(transformer.run(results))
        return results


class Transformer:
    """Base class for transforming raw image data."""

    def __init__(self, src_conn):
        """Initialize the transformer."""
        self.src_conn = src_conn

    def run(self, data):
        """Transform the raw data."""
        raise NotImplementedError


class TransformerAWS(Transformer):
    """Transform raw AWS data."""

    def run(self, data):
        """Transform the raw data."""
        # Verify that the data is from AWS.
        entries = [x for x in data if x.is_provided_by("aws") and x.is_raw()]

        results = []
        for entry in entries:
            raw = self.src_conn.get_content(entry)
            region = os.path.basename(raw.filename).split(".")[0]

            for content in raw.content:
                if content["OwnerId"] != config.AWS_RHEL_OWNER_ID:
                    continue

                image_data = aws.format_image(content, region)
                image_name = image_data["name"].replace(" ", "_").lower()
                data_entry = connection.DataEntry(
                    f"aws/{region}/{image_name}", image_data
                )
                results.append(data_entry)

        return results


class TransformerGOOGLE(Transformer):
    """Transform raw GCP data."""

    def run(self, data):
        """Transform the raw data."""
        entries = [x for x in data if x.is_provided_by("google") and x.is_raw()]

        results = []
        for e in entries:
            raw = self.src_conn.get_content(e)
            for content in raw.content:
                content["creation_timestamp"] = content["creationTimestamp"]
                if content["name"].__contains__("rhel"):
                    r = google.format_image(content)
                    de = connection.DataEntry(
                        "google/" + "global/" + r["name"].replace(" ", "_").lower(), r
                    )
                    results.append(de)

        return results


class TransformerAZURE(Transformer):
    """Transform raw Azure data."""

    def run(self, data):
        """Transform the raw data."""
        # Verify that the data is from Azure.
        entries = [x for x in data if x.is_provided_by("azure") and x.is_raw()]

        results = []
        for entry in entries:
            raw = self.src_conn.get_content(entry)
            region = os.path.basename(raw.filename).split(".")[0]

            for content in raw.content:
                # TODO: Solve bug: the data parsing for this one version didn't work
                if (
                    content["publisher"] != "RedHat"
                    or content["version"] == "8.2.2020270811"
                ):
                    continue

                content["hyperVGeneration"] = "unknown"

                image_data = azure.format_image(content)
                image_name = image_data["name"].replace(" ", "_").lower()
                data_entry = connection.DataEntry(
                    f"azure/{region}/{image_name}", image_data
                )

                results.append(data_entry)

        return results
