from typing import Callable

from cloudimagedirectory import config
from cloudimagedirectory.connection import connection
from cloudimagedirectory.update_images import aws
from cloudimagedirectory.update_images import azure


class Pipeline:
    transformer: list[Callable] = []
    src_conn = None

    def __init__(self, src_conn, transformer_funcs: list[Callable]):
        self.src_conn = src_conn
        for f in transformer_funcs:
            self.transformer.append(f(self.src_conn))

    def run(self, data):
        results = []
        for t in self.transformer:
            results.extend(t.run(data))
        return results


class Transformer:
    src_conn = None

    def __init__(self, src_conn):
        self.src_conn = src_conn

    def run(self, data):
        pass


class TransformerAWS(Transformer):
    def __init__(self, src_conn):
        super().__init__(src_conn)

    def run(self, data):
        entries = []
        for d in data:
            if d.filename.__contains__("aws"):
                entries.append(d)

        results = []
        for e in entries:
            raw = self.src_conn.get_content(e)
            region = raw.filename.split("/")
            region = region[len(region) - 1]
            region = region.split(".")[0]
            for content in raw.content:
                if content["OwnerId"] != config.AWS_RHEL_OWNER_ID:
                    continue
                r = aws.format_image(content, region)
                de = connection.DataEntry(
                    "aws/" + region + "/" + r["name"].replace(" ", "_").lower(), r
                )
                results.append(de)

        return results


class TransformerGOOGLE(Transformer):
    def __init__(self, src_conn):
        super().__init__(src_conn)

    def run(self, data):
        return []


class TransformerAZURE(Transformer):
    def __init__(self, src_conn):
        super().__init__(src_conn)

    def run(self, data):
        entries = []
        for d in data:
            if d.filename.__contains__("azure"):
                entries.append(d)

        results = []
        for e in entries:
            raw = self.src_conn.get_content(e)
            region = raw.filename.split("/")
            region = region[len(region) - 1]
            region = region.split(".")[0]
            for content in raw.content:
                # TODO: Solve bug: the data parsing for this one version didn't work
                if (
                    content["publisher"] != "RedHat"
                    or content["version"] == "8.2.2020270811"
                ):
                    continue
                content["hyperVGeneration"] = "unknown"
                r = azure.format_image(content)
                de = connection.DataEntry(
                    "azure/" + region + "/" + r["name"].replace(" ", "_").lower(), r
                )

                results.append(de)

        return results
