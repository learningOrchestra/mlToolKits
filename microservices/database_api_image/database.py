from bson.json_util import dumps
import json


class Dataset:
    ROW_ID = "_id"
    METADATA_ROW_ID = 0

    def __init__(self, database, file_manager):
        self.database_connector = database
        self.file_manager = file_manager

    def add_file(self, url, filename):
        self.file_manager.save_file(filename, url)

    def read_file(self, filename, skip, limit, query):
        result = []

        query_object = json.loads(query)
        skip = int(skip)
        limit = int(limit)

        for file in self.database_connector.find_in_file(
                filename, query_object, skip, limit
        ):
            result.append(json.loads(dumps(file)))

        return result

    def delete_file(self, filename):
        self.database_connector.delete_file(filename)

    def get_files(self, file_type):
        result = []

        for file in self.database_connector.get_filenames():
            metadata_file = self.database_connector.find_one_in_file(
                file, {self.ROW_ID: self.METADATA_ROW_ID, "type": file_type}
            )
            if metadata_file is None:
                continue
            metadata_file.pop(self.ROW_ID)
            result.append(metadata_file)

        return result
