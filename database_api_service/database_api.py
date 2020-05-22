import os
from pymongo import MongoClient, errors
from bson.json_util import dumps
import requests
from contextlib import closing
import csv
import json
import codecs


DATABASE_URL = "DATABASE_URL"
DATABASE_PORT = "DATABASE_PORT"


class DatabaseApi:
    MESSAGE_INVALID_URL = "invalid_url"
    MESSAGE_DUPLICATE_FILE = "duplicate_file"
    MESSAGE_CREATED_FILE = "file_created"
    MESSAGE_DELETED_FILE = "deleted_file"

    def __init__(self):
        self.mongo_client = MongoClient(
                os.environ[DATABASE_URL],
                int(os.environ[DATABASE_PORT]))
        self.database = self.mongo_client.database

    def add_file(self, url, filename):
        result = []
        try:
            with closing(requests.get(url, stream=True)) as r:
                reader = csv.reader(
                    codecs.iterdecode(r.iter_lines(), encoding='utf-8'),
                    delimiter=',', quotechar='"')

                count = 1
                file_collection = self.database[filename]
                headers = next(reader)

                for row in reader:
                    json_object = {headers[indice]: row[indice]
                                   for indice
                                   in range(len(headers))}

                    json_object["_id"] = count
                    file_collection.insert_one(json_object)
                    count += 1

        except requests.exceptions.RequestException:
            return DatabaseApi.MESSAGE_INVALID_URL

        except errors.PyMongoError:
            return DatabaseApi.MESSAGE_DUPLICATE_FILE

        return DatabaseApi.MESSAGE_CREATED_FILE

    def read_file(self, filename, skip, limit, query):
        result = []
        file_collection = self.database[filename]

        for file in file_collection.find(query).skip(skip).limit(limit):
            result.append(json.loads(dumps(file)))

        return result

    def delete_file(self, filename):
        file_collection = self.database[filename]
        file_collection.drop()
        return DatabaseApi.MESSAGE_DELETED_FILE

    def get_files(self):
        result = []

        for item in self.database.list_collection_names():
            result.append(item)

        return result
