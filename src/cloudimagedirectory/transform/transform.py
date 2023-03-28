"""Transforms the raw data into useful data."""
import os

from datetime import datetime
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


class TransformerIdxListImageLatest(Transformer):
    """Sort the transformed data, to have the latest images."""

    chunk_size = 50

    def run(self, data):
        """Sort the raw data."""
        # Verify that the data is not raw.
        entries = [x for x in data if not x.is_raw()]

        # Sort the list of data by date
        entries.sort(
            key=lambda x: datetime.strptime(
                "".join(x.content["date"].split("T")[0]), "%Y-%m-%d"
            ),
            reverse=True,
        )

        list = []
        for entry in entries:
            provider = "unknown"
            if entry.is_provided_by("aws"):
                provider = "aws"
            elif entry.is_provided_by("azure"):
                provider = "azure"
            elif entry.is_provided_by("google"):
                provider = "google"

            list.append(
                {
                    "name": entry.content["name"],
                    "date": entry.content["date"].split("T")[0],
                    "provider": provider,  # TODO: Evaluate if this can be removed
                    "ref": entry.filename,
                    "arch": entry.content["arch"],
                }
            )

        # Split the list of images into equally sized chunkes
        chunked_list = []
        chunk = []
        for i, item in enumerate(list, 1):
            chunk.append(item)
            if len(list) == i or i % self.chunk_size == 0:
                chunked_list.append(chunk)
                chunk = []

        results = []
        for page in range(0, len(chunked_list)):
            data_entry = connection.DataEntry(
                f"idx/list/sort-by-date/{page}", chunked_list[page]
            )
            results.append(data_entry)

        return results


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
        for entry in entries:
            raw = self.src_conn.get_content(entry)
            for content in raw.content:
                content["creation_timestamp"] = content["creationTimestamp"]
                if "rhel" in content["name"]:
                    image_data = google.format_image(content)
                    image_name = image_data["name"].replace(" ", "_").lower()
                    data_entry = connection.DataEntry(
                        f"google/global/{image_name}", image_data
                    )
                    results.append(data_entry)

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
                if content["publisher"] != "RedHat":
                    continue

                content["hyperVGeneration"] = "unknown"

                try:
                    image_data = azure.format_image(content)
                    image_name = image_data["name"].replace(" ", "_").lower()
                    data_entry = connection.DataEntry(
                        f"azure/{region}/{image_name}", image_data
                    )

                    results.append(data_entry)
                except:
                    print("Could not format image, sku: " + content["sku"] + " offer: " + content["offer"])


        return results
