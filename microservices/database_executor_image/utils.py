from datetime import datetime
import pytz
from pymongo import MongoClient
from inspect import signature, getmembers
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

        database_projection_query = {
            ID_FIELD_NAME: False
        }
        return list(self.__database[filename].find(
            filter=database_documents_query,
            projection=database_projection_query))

    def insert_one_in_file(self, filename: str, json_object: dict) -> None:
        file_collection = self.__database[filename]
        file_collection.insert_one(json_object)

    def insert_many_in_file(self, filename: str, json_object: object) -> None:
        file_collection = self.__database[filename]
        file_collection.insert_many(json_object)

    def delete_data_in_file(self, filename: str) -> None:
        file_collection = self.__database[filename]
        database_documents_query = {
            ID_FIELD_NAME: {"$ne": METADATA_DOCUMENT_ID}}

        file_collection.delete_many(filter=database_documents_query)

    def get_filenames(self) -> list:
        return self.__database.list_collection_names()

    def update_one(self, filename: str, new_value: dict, query: dict) -> None:
        new_values_query = {"$set": new_value}
        file_collection = self.__database[filename]
        file_collection.update_one(query, new_values_query)

    def delete_file(self, filename: str) -> None:
        file_collection = self.__database[filename]
        file_collection.drop()

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

    def create_file(self,
                    filename: str,
                    module_path: str,
                    class_name: str,
                    class_parameters: dict,
                    service_type: str) -> dict:
        metadata = self.__metadata_document.copy()
        metadata[NAME_FIELD_NAME] = filename
        metadata[MODULE_PATH_FIELD_NAME] = module_path
        metadata[CLASS_FIELD_NAME] = class_name
        metadata[CLASS_PARAMETERS_FIELD_NAME] = class_parameters
        metadata[TYPE_PARAM_NAME] = service_type
        metadata[EXECUTIONS_FIELD_NAME] = []

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
                                  method_name: str,
                                  method_parameters: dict,
                                  exception: str = None) -> None:
        document_query = {
            ID_FIELD_NAME: METADATA_DOCUMENT_ID
        }

        model_document = {
            "$push": {
                EXECUTIONS_FIELD_NAME: {
                    EXCEPTION_FIELD_NAME: exception,
                    DESCRIPTION_FIELD_NAME: description,
                    METHOD_FIELD_NAME: method_name,
                    METHOD_PARAMETERS_FIELD_NAME: method_parameters}
            }
        }
        self.__database_connector.update_one(
            executor_name,
            model_document,
            document_query
        )


class UserRequest:
    __MESSAGE_DUPLICATE_FILE = "duplicated name"
    __MESSAGE_INVALID_MODULE_PATH_NAME = "invalid module path name"
    __MESSAGE_INVALID_METHOD_NAME = "invalid method name"
    __MESSAGE_INVALID_CLASS_METHOD_PARAMETER = "invalid class method parameter"
    __MESSAGE_NONEXISTENT_FILE = "parentName doesn't exist"
    __MESSAGE_INVALID_CLASS_NAME = "invalid class name"
    __MESSAGE_INVALID_CLASS_PARAMETER = "invalid class parameter"

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

        class_members = getmembers(module_class)
        class_methods = [method[FIRST_ARGUMENT] for method in class_members]

        if method_name not in class_methods:
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

    def available_module_path_validator(self, package: str) -> None:
        try:
            importlib.import_module(package)

        except Exception:
            raise Exception(self.__MESSAGE_INVALID_MODULE_PATH_NAME)

    def valid_class_validator(self, tool_name: str, function_name: str) -> None:
        try:
            module = importlib.import_module(tool_name)
            getattr(module, function_name)

        except Exception:
            raise Exception(self.__MESSAGE_INVALID_CLASS_NAME)

    def valid_class_parameters_validator(self, tool: str, function: str,
                                         function_parameters: dict) -> None:
        module = importlib.import_module(tool)
        module_function = getattr(module, function)
        valid_function_parameters = signature(module_function.__init__)

        for parameter, value in function_parameters.items():
            if parameter not in valid_function_parameters.parameters:
                raise Exception(self.__MESSAGE_INVALID_CLASS_PARAMETER)


class Data:
    def __init__(self, database: Database, filename):
        self.__database = database
        self.__METADATA_QUERY = {ID_FIELD_NAME: METADATA_DOCUMENT_ID}
        self.filename = filename

    def get_module_and_class(self) -> tuple:
        model_metadata = self.__database.find_one(
            self.filename,
            self.__METADATA_QUERY)

        module_path = model_metadata[MODULE_PATH_FIELD_NAME]
        class_name = model_metadata[CLASS_FIELD_NAME]

        return module_path, class_name

    def get_class_parameters(self) -> dict:
        model_metadata = self.__database.find_one(
            self.filename,
            self.__METADATA_QUERY)

        return model_metadata[CLASS_PARAMETERS_FIELD_NAME]
