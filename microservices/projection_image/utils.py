from datetime import datetime
import pytz
from pymongo import MongoClient


class Metadata:
    def __init__(self, database):
        self.database_connector = database
        self.timezone_london = pytz.timezone("Etc/Greenwich")
        self.metadata_document = {
            "_id": 0,
            "type": "transform/projection",
            "finished": False,
        }

    def create_file(self, projection_filename, parent_filename, fields):
        london_time = datetime.now(self.timezone_london)
        now_time = london_time.strftime("%Y-%m-%dT%H:%M:%S-00:00")

        metadata = self.metadata_document.copy()
        metadata["timeCreated"] = now_time
        metadata["datasetName"] = projection_filename
        metadata["parentDatasetName"] = parent_filename
        metadata["fields"] = fields

        self.database_connector.insert_one_in_file(
            projection_filename,
            metadata)

        return metadata

    def update_finished_flag(self, filename, flag):
        flag_true_query = {"finished": flag}
        metadata_file_query = {"_id": 0}
        self.database_connector.update_one(filename,
                                           flag_true_query,
                                           metadata_file_query)


class Database:
    def __init__(self, database_url, replica_set, database_port, database_name):
        self.mongo_client = MongoClient(
            f'{database_url}/?replicaSet={replica_set}', int(database_port))
        self.database = self.mongo_client[database_name]

    def find_one(self, filename, query):
        file_collection = self.database[filename]
        return file_collection.find_one(query)

    def insert_one_in_file(self, filename, json_object):
        file_collection = self.database[filename]
        file_collection.insert_one(json_object)

    def get_filenames(self):
        return self.database.list_collection_names()

    def update_one(self, filename, new_value, query):
        new_values_query = {"$set": new_value}
        file_collection = self.database[filename]
        file_collection.update_one(query, new_values_query)

    @staticmethod
    def collection_database_url(database_url,
                                database_name,
                                database_filename,
                                database_replica_set
                                ):
        return f'{database_url}/{database_name}.{database_filename}' \
               f'?replicaSet={database_replica_set}&authSource=admin'


class UserRequest:
    MESSAGE_INVALID_FIELDS = "invalid fields"
    MESSAGE_INVALID_FILENAME = "invalid dataset name"
    MESSAGE_DUPLICATE_FILE = "duplicated projection name"
    MESSAGE_MISSING_FIELDS = "missing fields"
    MESSAGE_UNFINISHED_PROCESSING = "unfinished processing in input dataset"

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

    def projection_filename_validator(self, projection_filename):
        filenames = self.database.get_filenames()

        if projection_filename in filenames:
            raise Exception(self.MESSAGE_DUPLICATE_FILE)

    def projection_fields_validator(self, filename, projection_fields):
        if not projection_fields:
            raise Exception(self.MESSAGE_MISSING_FIELDS)

        filename_metadata_query = {"datasetName": filename}

        filename_metadata = self.database.find_one(filename,
                                                   filename_metadata_query)

        for field in projection_fields:
            if field not in filename_metadata["fields"]:
                raise Exception(self.MESSAGE_INVALID_FIELDS)
