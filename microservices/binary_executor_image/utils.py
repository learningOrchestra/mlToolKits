from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import pytz
from pymongo import MongoClient
from inspect import signature, getmembers
import importlib
from constants import Constants
import pandas as pd
import dill
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

    def get_entire_collection(self, filename: str) -> list:
        database_documents_query = {
            Constants.ID_FIELD_NAME: {"$ne": Constants.METADATA_DOCUMENT_ID}}

        database_projection_query = {
            Constants.ID_FIELD_NAME: False
        }
        return list(self.__database[filename].find(
            filter=database_documents_query,
            projection=database_projection_query))

    def get_field_from_collection(self, filename: str, field: str) -> list:
        database_documents_query = {
            Constants.ID_FIELD_NAME: {"$ne": Constants.METADATA_DOCUMENT_ID}}

        database_projection_query = {
            field: True,
            Constants.ID_FIELD_NAME: False
        }
        return list(self.__database[filename].find(
            filter=database_documents_query,
            projection=database_projection_query))

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

    def create_file(self, parent_name: str,
                    filename: str,
                    module_path: str,
                    class_name: str,
                    class_method: str,
                    service_type: str) -> dict:
        metadata = self.__metadata_document.copy()
        metadata[Constants.PARENT_NAME_FIELD_NAME] = parent_name
        metadata[Constants.NAME_FIELD_NAME] = filename
        metadata[Constants.METHOD_FIELD_NAME] = class_method
        metadata[Constants.TYPE_FIELD_NAME] = service_type
        metadata[Constants.MODULE_PATH_FIELD_NAME] = module_path
        metadata[Constants.CLASS_FIELD_NAME] = class_name

        self.__database_connector.insert_one_in_file(
            filename,
            metadata)

        return metadata

    def read_metadata(self, parent_name: str) -> object:
        metadata_query = {
            Constants.ID_FIELD_NAME: Constants.METADATA_DOCUMENT_ID}
        return self.__database_connector.find_one(parent_name, metadata_query)

    def update_finished_flag(self, filename: str, flag: bool) -> None:
        flag_true_query = {Constants.FINISHED_FIELD_NAME: flag}
        metadata_file_query = {
            Constants.ID_FIELD_NAME: Constants.METADATA_DOCUMENT_ID}
        self.__database_connector.update_one(filename,
                                             flag_true_query,
                                             metadata_file_query)

    def create_execution_document(self, executor_name: str,
                                  description: str,
                                  method_parameters: dict,
                                  exception: str = None) -> None:
        document_id_query = {
            Constants.ID_FIELD_NAME: {
                "$exists": True
            }
        }
        highest_id_sort = [(Constants.ID_FIELD_NAME, -1)]
        highest_id_document = self.__database_connector.find_one(
            executor_name, document_id_query, highest_id_sort)

        highest_id = highest_id_document[Constants.ID_FIELD_NAME]

        model_document = {
            Constants.EXCEPTION_FIELD_NAME: exception,
            Constants.DESCRIPTION_FIELD_NAME: description,
            Constants.METHOD_PARAMETERS_FIELD_NAME: method_parameters,
            Constants.ID_FIELD_NAME: highest_id + 1
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

        class_members = getmembers(module_class)
        class_methods = [method[Constants.FIRST_ARGUMENT] for method in
                         class_members]

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


class ObjectStorage:
    __WRITE_MODEL_OBJECT_OPTION = "wb"
    __READ_MODEL_OBJECT_OPTION = "rb"

    def __init__(self, database_connector: Database = None):
        self.__database_connector = database_connector
        self.__thread_pool = ThreadPoolExecutor()

    def save(self, instance: object, filename: str, service_type: str) -> None:
        model_output_path = ObjectStorage.get_write_binary_path(
            filename, service_type)
        if not os.path.exists(os.path.dirname(model_output_path)):
            os.makedirs(os.path.dirname(model_output_path))

        model_output = open(model_output_path,
                            self.__WRITE_MODEL_OBJECT_OPTION)
        dill.dump(instance, model_output)
        model_output.close()

    def delete(self, filename: str, service_type: str) -> None:
        self.__thread_pool.submit(self.__database_connector.delete_file,
                                  filename)
        self.__thread_pool.submit(
            os.remove,
            ObjectStorage.get_write_binary_path(filename, service_type))

    def read(self, filename, service_type: str) -> object:
        model_binary_instance = open(
            ObjectStorage.get_read_binary_path(
                filename, service_type),
            self.__READ_MODEL_OBJECT_OPTION)
        return dill.load(model_binary_instance)

    @staticmethod
    def get_write_binary_path(filename: str, service_type: str) -> str:
        return f'{os.environ[Constants.BINARY_VOLUME_PATH]}/' \
               f'{service_type}/{filename}'

    @staticmethod
    def get_read_binary_path(filename: str, service_type: str) -> str:
        if service_type == Constants.MODEL_TENSORFLOW_TYPE or \
                service_type == Constants.MODEL_SCIKITLEARN_TYPE:
            return f'{os.environ[Constants.MODELS_VOLUME_PATH]}/{filename}'
        elif service_type == Constants.TRANSFORM_TENSORFLOW_TYPE or \
                service_type == Constants.TRANSFORM_SCIKITLEARN_TYPE:
            return f'{os.environ[Constants.TRANSFORM_VOLUME_PATH]}/{filename}'
        elif service_type == Constants.PYTHON_FUNCTION_TYPE:
            return f'{os.environ[Constants.CODE_EXECUTOR_VOLUME_PATH]}/{filename}'
        else:
            return f'{os.environ[Constants.BINARY_VOLUME_PATH]}/' \
                   f'{service_type}/{filename}'


class Data:
    def __init__(self, database: Database, storage: ObjectStorage):
        self.__database = database
        self.__storage = storage
        self.__METADATA_QUERY = {
            Constants.ID_FIELD_NAME: Constants.METADATA_DOCUMENT_ID}

    def get_module_and_class_from_a_instance(self,
                                             name: str) -> tuple:

        model_types = [Constants.MODEL_TENSORFLOW_TYPE,
                       Constants.MODEL_SCIKITLEARN_TYPE]
        while self.get_type(name) not in model_types:
            instance_metadata = self.__database.find_one(
                name,
                self.__METADATA_QUERY)

            print(instance_metadata, flush=True)
            name = instance_metadata[Constants.PARENT_NAME_FIELD_NAME]

        model_metadata = self.__database.find_one(
            name,
            self.__METADATA_QUERY)

        module_path = model_metadata[Constants.MODULE_PATH_FIELD_NAME]
        class_name = model_metadata[Constants.CLASS_FIELD_NAME]

        return module_path, class_name

    def get_module_and_class_from_a_executor_name(self,
                                                  train_name: str) -> tuple:
        train_metadata = self.__database.find_one(
            train_name,
            self.__METADATA_QUERY)

        model_name = train_metadata[Constants.PARENT_NAME_FIELD_NAME]

        model_metadata = self.__database.find_one(
            model_name,
            self.__METADATA_QUERY)

        module_path = model_metadata[Constants.MODULE_PATH_FIELD_NAME]
        class_name = model_metadata[Constants.CLASS_FIELD_NAME]

        return module_path, class_name

    def get_class_method_from_a_executor_name(
            self, train_name: str) -> str:
        train_metadata = self.__database.find_one(
            train_name,
            self.__METADATA_QUERY)

        return train_metadata[Constants.METHOD_FIELD_NAME]

    def get_model_name_from_a_child(
            self, train_name: str) -> str:
        train_metadata = self.__database.find_one(
            train_name,
            self.__METADATA_QUERY)

        return train_metadata[Constants.PARENT_NAME_FIELD_NAME]

    def get_type(self, filename: str) -> str:
        metadata = self.__database.find_one(
            filename,
            self.__METADATA_QUERY)

        return metadata[Constants.TYPE_FIELD_NAME]

    def get_dataset_content(self, filename: str) -> object:
        if self.__is_stored_in_volume(filename):
            service_type = self.get_type(filename)
            return self.__storage.read(filename, service_type)
        else:
            dataset = self.__database.get_entire_collection(
                filename)

            return pd.DataFrame(dataset)

    def get_object_from_dataset(self, filename: str,
                                object_name: str) -> object:
        service_type = self.get_type(filename)
        instance = self.__storage.read(filename, service_type)
        return instance[object_name]

    def __is_stored_in_volume(self, filename: str) -> bool:
        volume_types = [
            Constants.MODEL_TENSORFLOW_TYPE,
            Constants.MODEL_SCIKITLEARN_TYPE,
            Constants.TUNE_TENSORFLOW_TYPE,
            Constants.TUNE_SCIKITLEARN_TYPE,
            Constants.TRAIN_TENSORFLOW_TYPE,
            Constants.TRAIN_SCIKITLEARN_TYPE,
            Constants.EVALUATE_TENSORFLOW_TYPE,
            Constants.EVALUATE_SCIKITLEARN_TYPE,
            Constants.PREDICT_TENSORFLOW_TYPE,
            Constants.PREDICT_SCIKITLEARN_TYPE,
            Constants.PYTHON_FUNCTION_TYPE,
            Constants.TRANSFORM_SCIKITLEARN_TYPE,
            Constants.TRANSFORM_TENSORFLOW_TYPE,
        ]

        return self.get_type(filename) in volume_types
