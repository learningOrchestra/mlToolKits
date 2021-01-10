from datetime import datetime
import pytz
from pymongo import MongoClient
from inspect import signature
import importlib
from constants import *


class Database:
    def __init__(self, database_url: str, replica_set: str, database_port: int,
                 database_name: str):
        self.__mongo_client = MongoClient(
            database_url + '/?replicaSet=' + replica_set, database_port)
        self.__database = self.__mongo_client[database_name]

    def find_one(self, filename: str, query: dict, sort: list = []):
        file_collection = self.__database[filename]
        return file_collection.find_one(query, sort=sort)

    def get_entire_collection(self, filename: str) -> list:
        database_documents_query = {
            ID_FIELD_NAME: {"$ne": METADATA_DOCUMENT_ID}}
        return list(self.__database[filename].find(database_documents_query))

    def insert_one_in_file(self, filename: str, json_object: dict) -> None:
        file_collection = self.__database[filename]
        file_collection.insert_one(json_object)

    def get_filenames(self) -> list:
        return self.__database.list_collection_names()

    def update_one(self, filename: str, new_value: dict, query: dict) -> None:
        new_values_query = {"$set": new_value}
        file_collection = self.__database[filename]
        file_collection.update_one(query, new_values_query)

    @staticmethod
    def collection_database_url(
            database_url: str,
            database_name: str,
            database_filename: str,
            database_replica_set: str) -> str:
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
            FINISHED_FIELD_NAME: False,
        }

    def create_file(self, parent_name: str,
                    filename: str,
                    class_method: str,
                    service_type: str) -> dict:
        metadata = self.__metadata_document.copy()
        metadata[PARENT_NAME_FIELD_NAME] = parent_name
        metadata[NAME_FIELD_NAME] = filename
        metadata[METHOD_FIELD_NAME] = class_method
        metadata[TYPE_FIELD_NAME] = service_type

        self.__database_connector.insert_one_in_file(
            filename,
            metadata)

        return metadata

    def read_metadata(self, parent_name: str) -> object:
        metadata_query = {ID_FIELD_NAME: METADATA_DOCUMENT_ID}
        return self.__database_connector.find_one(parent_name, metadata_query)

    def update_finished_flag(self, filename: str, flag: bool) -> None:
        flag_true_query = {FINISHED_FIELD_NAME: flag}
        metadata_file_query = {ID_FIELD_NAME: METADATA_DOCUMENT_ID}
        self.__database_connector.update_one(filename,
                                             flag_true_query,
                                             metadata_file_query)

    def create_execution_document(self, executor_name: str,
                                  description: str,
                                  method_parameters: dict) -> None:
        document_id_query = {
            ID_FIELD_NAME: {
                "$exists": True
            }
        }
        highest_id_sort = [(ID_FIELD_NAME, -1)]
        highest_id_document = self.__database_connector.find_one(
            executor_name, document_id_query, highest_id_sort)

        highest_id = highest_id_document[ID_FIELD_NAME]

        model_document = {
            DESCRIPTION_FIELD_NAME: description,
            METHOD_PARAMETERS_FIELD_NAME: method_parameters,
            ID_FIELD_NAME: highest_id + 1
        }
        self.__database_connector.insert_one_in_file(
            executor_name,
            model_document)


class UserRequest:
    __MESSAGE_DUPLICATE_FILE = "duplicated name"
    __MESSAGE_INVALID_MODULE_PATH_NAME = "invalid module path name"
    __MESSAGE_INVALID_METHOD_NAME = "invalid method name"
    __MESSAGE_INVALID_CLASS_METHOD_PARAMETER = "invalid class method parameter"
    __MESSAGE_NONEXISTENT_FILE = "parentName doesn't exist"

    def __init__(self, database_connector: Database):
        self.__database = database_connector

    def not_duplicated_filename_validator(self, filename: str) -> None:
        filenames = self.__database.get_filenames()

        if filename in filenames:
            raise Exception(self.__MESSAGE_DUPLICATE_FILE)

    def existent_filename_validator(self, filename: str) -> None:
        filenames = self.__database.get_filenames()

        if filename not in filenames:
            raise Exception(self.__MESSAGE_NONEXISTENT_FILE)

    def valid_method_class_validator(self, tool_name: str,
                                     class_name: str,
                                     method_name: str) -> None:
        module = importlib.import_module(tool_name)
        module_class = getattr(module, class_name)
        if method_name not in list(module_class.__dict__.keys()):
            raise Exception(self.__MESSAGE_INVALID_METHOD_NAME)

    def valid_method_parameters_validator(self, tool_name: str,
                                          class_name: str,
                                          class_method: str,
                                          method_parameters: dict) -> None:
        module = importlib.import_module(tool_name)
        module_class = getattr(module, class_name)
        class_method_reference = getattr(module_class, class_method)
        valid_function_parameters = signature(class_method_reference)

        for parameter, value in method_parameters.items():
            if parameter not in valid_function_parameters.parameters:
                raise Exception(self.__MESSAGE_INVALID_CLASS_METHOD_PARAMETER)


class Data:
    def __init__(self, database: Database):
        self.__database = database
        self.__METADATA_QUERY = {ID_FIELD_NAME: METADATA_DOCUMENT_ID}

    def get_module_and_class_from_a_model(self,
                                          model_name: str) -> tuple:
        model_metadata = self.__database.find_one(
            model_name,
            self.__METADATA_QUERY)

        module_path = model_metadata[MODULE_PATH_FIELD_NAME]
        class_name = model_metadata[CLASS_FIELD_NAME]

        return module_path, class_name

    def get_module_and_class_from_a_executor_name(self,
                                                  train_name: str) -> tuple:
        train_metadata = self.__database.find_one(
            train_name,
            self.__METADATA_QUERY)

        model_name = train_metadata[PARENT_NAME_FIELD_NAME]

        model_metadata = self.__database.find_one(
            model_name,
            self.__METADATA_QUERY)

        module_path = model_metadata[MODULE_PATH_FIELD_NAME]
        class_name = model_metadata[CLASS_FIELD_NAME]

        return module_path, class_name

    def get_class_method_from_a_executor_name(
            self, train_name: str) -> str:
        train_metadata = self.__database.find_one(
            train_name,
            self.__METADATA_QUERY)

        return train_metadata[METHOD_FIELD_NAME]

    def get_model_name_from_a_train(
            self, train_name: str) -> str:
        train_metadata = self.__database.find_one(
            train_name,
            self.__METADATA_QUERY)

        return train_metadata[PARENT_NAME_FIELD_NAME]
