from pymongo import MongoClient
from datetime import datetime
import pytz


class Metadata:
    def __init__(self, database):
        self.database_connector = database
        self.METADATA_DOCUMENT_ID = 0
        self.DOCUMENT_ID_NAME = "_id"

    def create_file(self, parent_filename, histogram_filename, fields):
        timezone_london = pytz.timezone("Etc/Greenwich")
        london_time = datetime.now(timezone_london)

        metadata_histogram_filename = {
            "parentDatasetName": parent_filename,
            "fields": fields,
            "datasetName": histogram_filename,
            "type": "histogram",
            self.DOCUMENT_ID_NAME: self.METADATA_DOCUMENT_ID,
            "finished": False,
            "timeCreated": london_time.strftime("%Y-%m-%dT%H:%M:%S-00:00")
        }

        self.database_connector.insert_one_in_file(
            histogram_filename, metadata_histogram_filename
        )

    def update_finish_flag(self, histogram_filename, flag):
        metadata_finished_true_query = {"finished": flag}
        metadata_id_query = {
            self.DOCUMENT_ID_NAME: self.METADATA_DOCUMENT_ID}

        self.database_connector.update_one(histogram_filename,
                                           metadata_finished_true_query,
                                           metadata_id_query)


class Database:
    def __init__(self, database_url, replica_set, database_port, database_name):
        self.mongo_client = MongoClient(
            f'{database_url}/?replicaSet={replica_set}', int(database_port))
        self.database = self.mongo_client[database_name]

    def find(self, filename, query):
        file_collection = self.database[filename]
        return file_collection.find(query)

    def aggregate(self, filename, pipeline):
        file_collection = self.database[filename]
        return list(file_collection.aggregate(pipeline))

    def insert_one_in_file(self, filename, json_object):
        file_collection = self.database[filename]
        file_collection.insert_one(json_object)

    def get_filenames(self):
        return self.database.list_collection_names()

    def update_one(self, filename, new_value, query):
        new_values_query = {"$set": new_value}
        file_collection = self.database[filename]
        file_collection.update_one(query, new_values_query)

    def find_one(self, filename, query):
        file_collection = self.database[filename]
        return file_collection.find_one(query)


class UserRequest:
    MESSAGE_INVALID_FIELDS = "invalid fields"
    MESSAGE_INVALID_FILENAME = "invalid dataset name"
    MESSAGE_MISSING_FIELDS = "missing fields"
    MESSAGE_UNFINISHED_PROCESSING = "unfinished processing in input dataset"
    MESSAGE_DUPLICATE_FILE = "duplicated dataset name"

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

    def histogram_filename_validator(self, histogram_filename):
        filenames = self.database.get_filenames()

        if histogram_filename in filenames:
            raise Exception(self.MESSAGE_DUPLICATE_FILE)

    def fields_validator(self, filename, fields):
        if not fields:
            raise Exception(self.MESSAGE_MISSING_FIELDS)

        filename_metadata_query = {"datasetName": filename}

        filename_metadata = self.database.find_one(filename,
                                                   filename_metadata_query)

        for field in fields:
            if field not in filename_metadata["fields"]:
                raise Exception(self.MESSAGE_INVALID_FIELDS)
