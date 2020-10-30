from pymongo import MongoClient
from datetime import datetime
import pytz
from concurrent.futures import ThreadPoolExecutor


class DataTypeConverter:
    METADATA_DOCUMENT_ID = 0
    DOCUMENT_ID_NAME = "_id"
    STRING_TYPE = "string"
    NUMBER_TYPE = "number"

    def __init__(self, database_connector):
        self.database_connector = database_connector
        self.thread_pool = ThreadPoolExecutor()

    def field_converter(self, filename, field, field_type):
        query = {}
        for document in self.database_connector.find(filename, query):
            if document[self.DOCUMENT_ID_NAME] == self.METADATA_DOCUMENT_ID:
                continue

            values = {}
            if field_type == self.STRING_TYPE:
                if document[field] == str:
                    continue
                if document[field] is None:
                    values[field] = ""
                else:
                    values[field] = str(document[field])

            elif field_type == self.NUMBER_TYPE:
                if (
                        document[field] == int
                        or document[field] == float
                        or document[field] is None
                ):
                    continue
                if document[field] == "":
                    values[field] = None
                else:
                    values[field] = float(document[field])

                    if values[field].is_integer():
                        values[field] = int(values[field])

            self.database_connector.update_one(filename, values, document)

    def convert_existent_file(self, filename, fields_dictionary):

        self.update_finished_metadata_file(filename, False)

        self.thread_pool.submit(self.field_file_converter, filename,
                                fields_dictionary)

    def field_file_converter(self, filename, fields_dictionary):
        for field in fields_dictionary:
            self.field_converter(filename, field,
                                 fields_dictionary[field])

        self.update_finished_metadata_file(filename, True)

    def create_metadata_file(self, filename):
        timezone_london = pytz.timezone("Etc/Greenwich")
        london_time = datetime.now(timezone_london)

        metadata_file = {
            "filename": filename,
            "time_created": london_time.strftime("%Y-%m-%dT%H:%M:%S-00:00"),
            "_id": 0,
            "finished": False,
        }
        self.database_connector.insert_one_in_file(filename, metadata_file)

    def update_finished_metadata_file(self, filename, flag):
        metadata_file = {
            "finished": flag,
        }
        self.database_connector.update_one(filename, metadata_file)


class MongoOperations:
    def __init__(self, database_url, database_port, database_name):
        self.mongo_client = MongoClient(database_url, int(database_port))
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


class DataTypeHandlerRequestValidator:
    MESSAGE_INVALID_FIELDS = "invalid_fields"
    MESSAGE_INVALID_FILENAME = "invalid_filename"
    MESSAGE_MISSING_FIELDS = "missing_fields"
    STRING_TYPE = "string"
    NUMBER_TYPE = "number"

    def __init__(self, database_connector):
        self.database = database_connector

    def filename_validator(self, filename):
        filenames = self.database.get_filenames()

        if filename not in filenames:
            raise Exception(self.MESSAGE_INVALID_FILENAME)

    def fields_validator(self, filename, fields):
        if not fields:
            raise Exception(self.MESSAGE_MISSING_FIELDS)

        filename_metadata_query = {"filename": filename}

        filename_metadata = self.database.find_one(filename,
                                                   filename_metadata_query)

        for field in fields:
            if field not in filename_metadata["fields"]:
                raise Exception(self.MESSAGE_INVALID_FIELDS)

            if fields[field] != self.NUMBER_TYPE and fields[
                field] != self.STRING_TYPE:
                raise Exception(self.MESSAGE_INVALID_FIELDS)
