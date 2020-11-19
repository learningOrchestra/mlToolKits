from pymongo import errors
from bson.json_util import dumps
import requests
import json


class Dataset:
    MESSAGE_INVALID_URL = "invalid url"
    MESSAGE_DUPLICATE_FILE = "duplicate file"
    ROW_ID = "_id"
    METADATA_ROW_ID = 0

    def __init__(self, database_object, file_manager_object):
        self.database_object = database_object
        self.file_manager_object = file_manager_object

    def add_file(self, url, filename):
        try:
            self.file_manager_object.save_file(filename, url,
                                               self.database_object)

        except requests.exceptions.RequestException:
            raise Exception(self.MESSAGE_INVALID_URL)

        except errors.PyMongoError:
            raise Exception(self.MESSAGE_DUPLICATE_FILE)

    def read_file(self, filename, skip, limit, query):
        result = []

        query_object = json.loads(query)
        skip = int(skip)
        limit = int(limit)

        for file in self.database_object.find_in_file(
                filename, query_object, skip, limit
        ):
            result.append(json.loads(dumps(file)))

        return result

    def delete_file(self, filename):
        self.database_object.delete_file(filename)

    def get_files(self, file_type):
        result = []

        for file in self.database_object.get_filenames():
            metadata_file = self.database_object.find_one_in_file(
                file, {self.ROW_ID: self.METADATA_ROW_ID, "type": file_type}
            )
            if metadata_file is None:
                continue
            metadata_file.pop(self.ROW_ID)
            result.append(metadata_file)

        return result
