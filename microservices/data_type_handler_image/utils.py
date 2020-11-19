from pymongo import MongoClient
from datetime import datetime
import pytz


class Metadata:
    def __init__(self, database_connector):
        self.database_connector = database_connector

    def create_file(self, filename):
        timezone_london = pytz.timezone("Etc/Greenwich")
        london_time = datetime.now(timezone_london)

        metadata_file = {
            "datasetName": filename,
            "timeCreated": london_time.strftime("%Y-%m-%dT%H:%M:%S-00:00"),
            "_id": 0,
            "finished": False,
            "type": "dataType"
        }
        self.database_connector.insert_one_in_file(filename, metadata_file)

    def update_finished_flag(self, filename, flag):
        metadata_new_value = {
            "finished": flag,
        }
        metadata_query = {
            "_id": 0
        }
        self.database_connector.update_one(filename, metadata_new_value,
                                           metadata_query)


class Database:
    def __init__(self, database_url, replica_set, database_port, database_name):
        self.mongo_client = MongoClient(
            database_url + '/?replicaSet=' + replica_set, int(database_port))
        self.database = self.mongo_client[database_name]

    def find(self, filename, query):
        file_collection = self.database[filename]
        return file_collection.find(query)

    def get_filenames(self):
        return self.database.list_collection_names()

    def update_one(self, filename, new_value, query):
        new_values_query = {"$set": new_value}
        file_collection = self.database[filename]
        file_collection.update_one(query, new_values_query)

    def find_one(self, filename, query):
        file_collection = self.database[filename]
        return file_collection.find_one(query)

    def insert_one_in_file(self, filename, json_object):
        file_collection = self.database[filename]
        file_collection.insert_one(json_object)


class UserRequest:
    MESSAGE_INVALID_FIELDS = "invalid fields"
    MESSAGE_INVALID_FILENAME = "invalid dataset name"
    MESSAGE_MISSING_FIELDS = "missing fields"
    MESSAGE_UNFINISHED_PROCESSING = "unfinished processing in input dataset"
    STRING_TYPE = "string"
    NUMBER_TYPE = "number"

    def __init__(self, database_connector):
        self.database = database_connector

    def filename_validator(self, filename):
        filenames = self.database.get_filenames()

        if filename not in filenames:
            raise Exception(self.MESSAGE_INVALID_FILENAME)

    def finished_processing_validator(self, filename):
        filename_metadata_query = {"datasetName": filename}

        filename_metadata = self.database.find_one(filename,
                                                   filename_metadata_query)

        if not filename_metadata["finished"]:
            raise Exception(self.MESSAGE_UNFINISHED_PROCESSING)

    def fields_validator(self, filename, fields):
        if not fields:
            raise Exception(self.MESSAGE_MISSING_FIELDS)

        filename_metadata_query = {"datasetName": filename}

        filename_metadata = self.database.find_one(filename,
                                                   filename_metadata_query)

        for field in fields:
            if field not in filename_metadata["fields"]:
                raise Exception(self.MESSAGE_INVALID_FIELDS)

            if fields[field] != self.NUMBER_TYPE and \
                    fields[field] != self.STRING_TYPE:
                raise Exception(self.MESSAGE_INVALID_FIELDS)
