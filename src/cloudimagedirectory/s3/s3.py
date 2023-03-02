import boto3
import json

exception_not_connected = Exception("Client is not connected to s3 bucket")
exception_already_connected = Exception("Client is already connected to s3 bucket")


class Connection:
    def connect(self):
        pass

    def get_filenames(self):
        pass

    def get_content(self, filename):
        pass
    
    def put_content(self, content, filename):
        pass

class DataEntry:
    filename = ""
    content = None

    def __init__(self, filename, content):
        self.filename = filename
        self.content = content

    def to_bytes(self):
        return ' '.join(format(x, 'b') for x in bytearray(json.dumps(self.content), 'utf-8'))


class ConnectionAWS(Connection):
    id = ""
    access_key = ""
    origin_path = ""
    bucket = ""
    client = None

    def __init__(self, id, access_key, origin_path, bucket):
        self.id = id
        self.access_key = access_key
        self.origin_path = origin_path
        self.bucket = bucket

    def connect(self):
        if self.client is not None:
            raise exception_already_connected
        self.client = boto3.client('s3',
            aws_access_key_id=self.id,
            aws_secret_access_key=self.access_key
        )

    def get_filenames(self):
        if self.client is None:
            raise exception_not_connected
        paginator = self.client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=self.bucket, Prefix=self.origin_path)

        data_files = []

        for page in pages:
            for obj in page['Contents']:
                filename = obj['Key']
                if filename.endswith('json'):
                    data_files.append(DataEntry(filename, None))

        return data_files
    
    def get_content(self, data):
        if self.client is None:
            raise exception_not_connected
        obj = self.client.get_object(Bucket=self.bucket, Key=data.filename)
        j = json.loads(obj['Body'].read().decode('utf-8'))
        return DataEntry(data.filename, j)

    def put_content(self, data):
        if self.client is None:
            raise exception_not_connected
        try:
            print("try to upload: " + data.filename)
            self.client.put_object(Body=data.to_bytes(), Bucket=self.bucket, Key=data.filename)
        except Exception as e:
            print('Failed to upload to s3 bucket: '+ str(e))
