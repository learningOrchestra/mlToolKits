from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import pytz
from pymongo import MongoClient
from constants import Constants
import pandas as pd
import os
import dill
import traceback
from tensorflow import keras


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

    def insert_many_in_file(self, filename: str, json_object: object) -> None:
        file_collection = self.__database[filename]
        file_collection.insert_many(json_object)

    def delete_data_in_file(self, filename: str) -> None:
        file_collection = self.__database[filename]
        database_documents_query = {
            Constants.ID_FIELD_NAME: {"$ne": Constants.METADATA_DOCUMENT_ID}}

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

    def create_file(self,
                    filename: str, service_type: str) -> dict:
        metadata = self.__metadata_document.copy()
        metadata[Constants.NAME_FIELD_NAME] = filename
        metadata[Constants.TYPE_PARAM_NAME] = service_type

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
                                  function_parameters: dict,
                                  function_message: str,
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
            Constants.FUNCTION_MESSAGE_FIELD_NAME: function_message,
            Constants.DESCRIPTION_FIELD_NAME: description,
            Constants.FUNCTION_PARAMETERS_FIELD_NAME: function_parameters,
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
    __MESSAGE_NONEXISTENT_FILE = "parent name doesn't exist"
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


class ObjectStorage:
    __WRITE_OBJECT_OPTION = "wb"
    __READ_OBJECT_OPTION = "rb"

    def __init__(self, database_connector: Database):
        self.__database_connector = database_connector
        self.__thread_pool = ThreadPoolExecutor()

    def read(self, filename: str, service_type: str) -> object:
        binary_path = ObjectStorage.get_read_binary_path(
            filename, service_type)
        binary_instance = open(
            binary_path,
            self.__READ_OBJECT_OPTION)

        try:
            return dill.load(binary_instance)
        except Exception:
            traceback.print_exc()

        try:
            return keras.models.load_model(binary_path)
        except Exception:
            traceback.print_exc()

        return binary_instance

    def save(self, instance: object, filename: str) -> None:
        output_path = ObjectStorage.get_write_binary_path(filename)

        try:
            keras.models.save_model(instance, output_path)
        except Exception:
            traceback.print_exc()
            instance_output = open(output_path,
                                   self.__WRITE_OBJECT_OPTION)
            dill.dump(instance, instance_output)
            instance_output.close()

    def delete(self, filename: str) -> None:
        self.__thread_pool.submit(
            self.__database_connector.delete_file, filename)
        self.__thread_pool.submit(
            os.remove, ObjectStorage.get_write_binary_path(filename))

    @staticmethod
    def get_write_binary_path(filename: str) -> str:
        return f'{os.environ[Constants.CODE_EXECUTOR_VOLUME_PATH]}/{filename}'

    @staticmethod
    def get_read_binary_path(filename: str, service_type: str) -> str:
        if service_type == Constants.DATASET_GENERIC_TYPE:
            return f'{os.environ[Constants.DATASET_VOLUME_PATH]}/{filename}'
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

    def get_type(self, filename) -> str:
        metadata = self.__database.find_one(
            filename,
            self.__METADATA_QUERY)

        return metadata[Constants.TYPE_PARAM_NAME]

    def __is_stored_in_volume(self, filename) -> bool:
        volume_types = [
            Constants.DATASET_GENERIC_TYPE,
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
