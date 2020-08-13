from pymongo import MongoClient


class DatabaseInterface():
    def find(self, filename, query):
        pass

    def find_one(self, filename, query):
        pass

    def get_filenames(self):
        pass

    def insert_one_in_file(self, filename, json_object):
        pass

    def update_one(self, filename, new_value, query):
        pass


class RequestValidatorInterface():
    MESSAGE_INVALID_FIELDS = "invalid_fields"
    MESSAGE_INVALID_FILENAME = "invalid_filename"
    MESSAGE_MISSING_FIELDS = "missing_fields"
    MESSAGE_DUPLICATE_FILE = "duplicated_filename"

    def filename_validator(self, filename):
        pass

    def histogram_filename_validator(self, histogram_filename):
        pass

    def fields_validator(self, filename, fields):
        pass


class HistogramInterface():

    def create_histogram(self, filename, histogram_filename, fields):
        pass


class Histogram(HistogramInterface):
    METADATA_DOCUMENT_ID = 0
    DOCUMENT_ID_NAME = "_id"

    def __init__(self, database_connector):
        self.database_connector = database_connector

    def create_histogram(self, filename, histogram_filename, fields):
        metadata_histogram_filename = {
            "filename_parent": filename,
            "fields": fields,
            "filename": histogram_filename,
            "_id": 0
        }

        self.database_connector.insert_one_in_file(
            histogram_filename,
            metadata_histogram_filename)

        document_id = 1

        for field in fields:
            field_accumulator = "$" + field
            print(field_accumulator, flush=True)
            pipeline = [{
                "$group": {"_id": field_accumulator, "count": {"$sum": 1}}}]

            field_result = {
                field: self.database_connector.aggregate(
                    filename, pipeline),
                "_id": document_id}
            document_id += 1

            self.database_connector.insert_one_in_file(
                histogram_filename, field_result)


class MongoOperations(DatabaseInterface):
    def __init__(self, database_url, database_port, database_name):
        self.mongo_client = MongoClient(
            database_url,
            int(database_port))
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


class HistogramRequestValidator(RequestValidatorInterface):
    def __init__(self, database_connector):
        self.database = database_connector

    def filename_validator(self, filename):
        filenames = self.database.get_filenames()

        if(filename not in filenames):
            raise Exception(self.MESSAGE_INVALID_FILENAME)

    def histogram_filename_validator(self, histogram_filename):
        filenames = self.database.get_filenames()

        if(histogram_filename in filenames):
            raise Exception(self.MESSAGE_DUPLICATE_FILE)

    def fields_validator(self, filename, fields):
        if not fields:
            raise Exception(self.MESSAGE_MISSING_FIELDS)

        filename_metadata_query = {"filename": filename}

        filename_metadata = self.database.find_one(
            filename, filename_metadata_query)

        for field in fields:
            if field not in filename_metadata["fields"]:
                raise Exception(self.MESSAGE_INVALID_FIELDS)
