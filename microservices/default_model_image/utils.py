from datetime import datetime
import pytz
from pymongo import MongoClient
import inspect
import importlib
from constants import *


class Database:
    def __init__(self, database_url: str, replica_set: str, database_port: int,
                 database_name: str):
        self.__mongo_client = MongoClient(
            database_url + '/?replicaSet=' + replica_set, database_port)
        self.__database = self.__mongo_client[database_name]

    def find_one(self, filename: str, query: dict):
        file_collection = self.__database[filename]
        return file_collection.find_one(query)

    def insert_one_in_file(self, filename: str, json_object: dict):
        file_collection = self.__database[filename]
        file_collection.insert_one(json_object)

    def get_filenames(self) -> list:
        return self.__database.list_collection_names()

    def update_one(self, filename: str, new_value: dict, query: dict):
        new_values_query = {"$set": new_value}
        file_collection = self.__database[filename]
        file_collection.update_one(query, new_values_query)

    @staticmethod
    def collection_database_url(
            database_url: str, database_name: str, database_filename: str,
            database_replica_set: str
    ) -> str:
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


class Metadata:
    def __init__(self, database: Database):
        self.__database_connector = database
        __timezone_london = pytz.timezone("Etc/Greenwich")
        __london_time = datetime.now(__timezone_london)
        self.__now_time = __london_time.strftime("%Y-%m-%dT%H:%M:%S-00:00")

        self.__metadata_document = {
            "timeCreated": self.__now_time,
            ID_FIELD_NAME: METADATA_DOCUMENT_ID,
            "type": "defaultModel",
            FINISHED_FIELD_NAME: False,
        }

    def create_file(self, model_name: str,
                    module_path: str, class_name: str) -> dict:
        metadata = self.__metadata_document.copy()
        metadata[MODEL_FIELD_NAME] = model_name
        metadata[MODULE_PATH_FIELD_NAME] = module_path
        metadata[CLASS_FIELD_NAME] = class_name

        self.__database_connector.insert_one_in_file(
            model_name,
            metadata)

        return metadata

    def update_finished_flag(self, filename: str, flag: bool):
        flag_true_query = {FINISHED_FIELD_NAME: flag}
        metadata_file_query = {ID_FIELD_NAME: METADATA_DOCUMENT_ID}
        self.__database_connector.update_one(filename,
                                             flag_true_query,
                                             metadata_file_query)


class UserRequest:
    __MESSAGE_DUPLICATE_FILE = "duplicate file"
    __MESSAGE_INVALID_MODULE_PATH_NAME = "invalid module path name"
    __MESSAGE_INVALID_CLASS_NAME = "invalid class name"
    __MESSAGE_INVALID_CLASS_PARAMETER = "invalid class parameter"

    def __init__(self, database_connector: Database):
        self.__database = database_connector

    def not_duplicated_filename_validator(self, filename: str):
        filenames = self.__database.get_filenames()

        if filename in filenames:
            raise Exception(self.__MESSAGE_DUPLICATE_FILE)

    def available_module_path_validator(self, package: str):
        try:
            importlib.import_module(package)

        except Exception:
            raise Exception(self.__MESSAGE_INVALID_MODULE_PATH_NAME)

    def valid_class_validator(self, tool_name: str, function_name: str):
        try:
            module = importlib.import_module(tool_name)
            getattr(module, function_name)

        except Exception:
            raise Exception(self.__MESSAGE_INVALID_CLASS_NAME)

    def valid_class_parameters_validator(self, tool: str, function: str,
                                         function_parameters: dict):
        module = importlib.import_module(tool)
        module_function = getattr(module, function)
        valid_function_parameters = inspect.getfullargspec(module_function)

        for parameter, value in function_parameters:
            if parameter not in valid_function_parameters[FIRST_ARGUMENT]:
                raise Exception(self.__MESSAGE_INVALID_CLASS_PARAMETER)
