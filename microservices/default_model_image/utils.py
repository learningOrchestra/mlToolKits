from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import pytz
from pymongo import MongoClient
from inspect import signature
import importlib
from constants import Constants
import pickle
import os


class Database:
    def __init__(self, database_url: str, replica_set: str, database_port: int,
                 database_name: str):
        self.__mongo_client = MongoClient(
            f'{database_url}/?replicaSet={replica_set}', database_port)
        self.__database = self.__mongo_client[database_name]

    def find_one(self, filename: str, query: dict, sort: list = []):
        file_collection = self.__database[filename]
        return file_collection.find_one(query, sort=sort)

    def insert_one_in_file(self, filename: str, json_object: dict) -> None:
        file_collection = self.__database[filename]
        file_collection.insert_one(json_object)

    def get_filenames(self) -> list:
        return self.__database.list_collection_names()

    def update_one(self, filename: str, new_value: dict, query: dict) -> None:
        new_values_query = {"$set": new_value}
        file_collection = self.__database[filename]
        file_collection.update_one(query, new_values_query)

    def delete_file(self, filename: str) -> None:
        file_collection = self.__database[filename]
        file_collection.drop()


class Metadata:
    def __init__(self, database: Database):
        self.__database_connector = database
        __timezone_london = pytz.timezone("Etc/Greenwich")
        __london_time = datetime.now(__timezone_london)
        self.__now_time = __london_time.strftime("%Y-%m-%dT%H:%M:%S-00:00")

        self.__metadata_document = {
            "timeCreated": self.__now_time,
            Constants.ID_FIELD_NAME: Constants.METADATA_DOCUMENT_ID,
            Constants.FINISHED_FIELD_NAME: False,
        }

    def create_file(self, model_name: str, service_type: str,
                    module_path: str, class_name: str) -> dict:
        metadata = self.__metadata_document.copy()
        metadata[Constants.MODEL_FIELD_NAME] = model_name
        metadata[Constants.MODULE_PATH_FIELD_NAME] = module_path
        metadata[Constants.CLASS_FIELD_NAME] = class_name
        metadata[Constants.TYPE_PARAM_NAME] = service_type
        
        self.__database_connector.insert_one_in_file(
            model_name,
            metadata)

        return metadata

    def update_finished_flag(self, filename: str, flag: bool) -> None:
        flag_true_query = {Constants.FINISHED_FIELD_NAME: flag}
        metadata_file_query = {
            Constants.ID_FIELD_NAME: Constants.METADATA_DOCUMENT_ID}
        self.__database_connector.update_one(filename,
                                             flag_true_query,
                                             metadata_file_query)

    def create_model_document(self, model_name: str, description: str,
                              class_parameters: dict,
                              exception: str = None) -> None:
        document_id_query = {
            Constants.ID_FIELD_NAME: {
                "$exists": True
            }
        }
        highest_id_sort = [(Constants.ID_FIELD_NAME, -1)]
        highest_id_document = self.__database_connector.find_one(
            model_name, document_id_query, highest_id_sort)

        highest_id = highest_id_document[Constants.ID_FIELD_NAME]

        model_document = {
            Constants.EXCEPTION_FIELD_NAME: exception,
            Constants.DESCRIPTION_FIELD_NAME: description,
            Constants.CLASS_PARAMETERS_FIELD_NAME: class_parameters,
            Constants.ID_FIELD_NAME: highest_id + 1
        }
        self.__database_connector.insert_one_in_file(
            model_name,
            model_document)


class UserRequest:
    __MESSAGE_DUPLICATE_FILE = "duplicated model name"
    __MESSAGE_INVALID_MODULE_PATH_NAME = "invalid module path name"
    __MESSAGE_INVALID_CLASS_NAME = "invalid class name"
    __MESSAGE_INVALID_CLASS_PARAMETER = "invalid class parameter"
    __MESSAGE_NONEXISTENT_FILE = "model name doesn't exist"

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


class ObjectStorage:
    __WRITE_MODEL_OBJECT_OPTION = "wb"
    __READ_MODEL_OBJECT_OPTION = "rb"

    def __init__(self, database_connector: Database):
        self.__thread_pool = ThreadPoolExecutor()
        self.__database_connector = database_connector

    def save(self, filename: str, model_instance: object) -> None:
        model_output = open(ObjectStorage.get_binary_path(filename),
                            self.__WRITE_MODEL_OBJECT_OPTION)
        pickle.dump(model_instance, model_output)
        model_output.close()

    def delete(self, filename: str) -> None:
        self.__thread_pool.submit(self.__database_connector.delete_file,
                                  filename)
        self.__thread_pool.submit(os.remove,
                                  ObjectStorage.get_binary_path(filename))

    @staticmethod
    def get_binary_path(filename: str) -> str:
        return f'{os.environ[Constants.MODELS_VOLUME_PATH]}/{filename}'


class Data:
    def __init__(self, database: Database):
        self.__database = database
        self.__METADATA_QUERY = {
            Constants.ID_FIELD_NAME: Constants.METADATA_DOCUMENT_ID}

    def get_module_and_class_from_a_model(self, model_name: str) -> tuple:
        model_metadata = self.__database.find_one(
            model_name,
            self.__METADATA_QUERY)

        module_path = model_metadata[Constants.MODULE_PATH_FIELD_NAME]
        class_name = model_metadata[Constants.CLASS_FIELD_NAME]

        return module_path, class_name
