from cloudimagedirectory.connection import connection

class Pipeline:
    transformer = []
    src_conn = None

    def __init__(self, src_conn, transformer_funcs):
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
            raw_content = self.src_conn.get_content(e)
            print("content")
            print(raw_content.filename)
            print(raw_content.content)
            pass
            # TODO: transform content in schema
            # TODO: create data entries for schema files and return them

        return [connection.DataEntry("aws/eu-west1/rhel-test.json", "test-content")]

class TransformerGOOGLE(Transformer):
    def run(self, data):
        return []

class TransformerAZURE(Transformer):
    def run(self, data):
        return []
