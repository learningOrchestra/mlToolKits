from datetime import datetime
import pytz
from pymongo import MongoClient
import inspect
import importlib


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
            "_id": 0,
            "type": "defaultModel",
            "finished": False,
        }

    def create_file(self, model_name: str,
                    tool: str, function: str) -> dict:
        metadata = self.__metadata_document.copy()
        metadata["modelName"] = model_name
        metadata["tool"] = tool
        metadata["function"] = function

        self.__database_connector.insert_one_in_file(
            model_name,
            metadata)

        return metadata

    def update_finished_flag(self, filename: str, flag: bool):
        flag_true_query = {"finished": flag}
        metadata_file_query = {"_id": 0}
        self.__database_connector.update_one(filename,
                                             flag_true_query,
                                             metadata_file_query)


class UserRequest:
    __MESSAGE_DUPLICATE_FILE = "duplicate file"
    __MESSAGE_INVALID_TOOL_NAME = "invalid tool name"
    __MESSAGE_INVALID_FUNCTION_NAME = "invalid function name"
    __MESSAGE_INVALID_FUNCTION_PARAMETER = "invalid function parameter"

    def __init__(self, database_connector: Database):
        self.__database = database_connector

    def not_duplicated_filename_validator(self, filename: str):
        filenames = self.__database.get_filenames()

        if filename in filenames:
            raise Exception(self.__MESSAGE_DUPLICATE_FILE)

    def available_tool_name_validator(self, tool_name: str):
        try:
            importlib.import_module(tool_name)

        except Exception:
            raise Exception(self.__MESSAGE_INVALID_TOOL_NAME)

    def valid_function_validator(self, tool_name: str, function_name: str):
        try:
            importlib.import_module(tool_name)
            getattr(tool_name, function_name)

        except Exception:
            raise Exception(self.__MESSAGE_INVALID_FUNCTION_NAME)

    def valid_function_parameters_validator(self, tool: str, function: str,
                                            function_parameters: dict):
        module = importlib.import_module(tool)
        module_function = getattr(module, function)
        valid_function_parameters = inspect.getfullargspec(module_function)

        arguments_list_index = 0
        for parameter, value in function_parameters:
            if parameter not in valid_function_parameters[arguments_list_index]:
                raise Exception(self.__MESSAGE_INVALID_FUNCTION_PARAMETER)
