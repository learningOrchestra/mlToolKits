import os
from pymongo import MongoClient

IMAGES_PATH = "IMAGES_PATH"


class Database:
    def __init__(self, database_url, replica_set, database_port, database_name):
        self.mongo_client = MongoClient(
            database_url + '/?replicaSet=' + replica_set, int(database_port))
        self.database = self.mongo_client[database_name]

    def find_one(self, filename, query):
        file_collection = self.database[filename]
        return file_collection.find_one(query)

    def get_filenames(self):
        return self.database.list_collection_names()

    @staticmethod
    def collection_database_url(
            database_url, database_name, database_filename, database_replica_set
    ):
        return (
                database_url
                + "/"
                + database_name
                + "."
                + database_filename
                + "?replicaSet="
                + database_replica_set
                + "&authSource=admin"
        )


class UserRequest:
    MESSAGE_INVALID_FILENAME = "invalid dataset name"
    MESSAGE_DUPLICATE_FILE = "duplicated plot name"
    MESSAGE_INVALID_LABEL = "invalid field"
    MESSAGE_NOT_FOUND = "plot name doesn't found"
    MESSAGE_UNFINISHED_PROCESSING = "unfinished processing in input dataset"
    IMAGE_FORMAT = ".png"

    def __init__(self, database_connector):
        self.database = database_connector

    def parent_filename_validator(self, filename):
        filenames = self.database.get_filenames()

        if filename not in filenames:
            raise Exception(self.MESSAGE_INVALID_FILENAME)

    def finished_processing_validator(self, filename):
        filename_metadata_query = {"datasetName": filename}

        filename_metadata = self.database.find_one(filename,
                                                   filename_metadata_query)

        if not filename_metadata["finished"]:
            raise Exception(self.MESSAGE_UNFINISHED_PROCESSING)

    @staticmethod
    def tsne_filename_existence_validator(tsne_filename):
        images = os.listdir(os.environ[IMAGES_PATH])
        image_name = tsne_filename + UserRequest.IMAGE_FORMAT
        if image_name in images:
            raise Exception(UserRequest.MESSAGE_DUPLICATE_FILE)

    @staticmethod
    def tsne_filename_nonexistence_validator(tsne_filename):
        images = os.listdir(os.environ[IMAGES_PATH])
        image_name = tsne_filename + UserRequest.IMAGE_FORMAT

        if image_name not in images:
            raise Exception(UserRequest.MESSAGE_NOT_FOUND)

    def filename_label_validator(self, filename, label):
        if label is None:
            return

        filename_metadata_query = {"datasetName": filename}

        filename_metadata = self.database.find_one(filename,
                                                   filename_metadata_query)

        if label not in filename_metadata["fields"]:
            raise Exception(self.MESSAGE_INVALID_LABEL)
