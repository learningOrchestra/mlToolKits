from concurrent.futures import ThreadPoolExecutor
from utils import *
from constants import *
from io import StringIO
import sys
import validators
import requests


class Function:
    def treat(self, function: str) -> str:
        if self.__is_url(function):
            function = self.__get_data_from_url(function)
        return function

    def __is_url(self, value: str) -> bool:
        return validators.url(value)

    def __get_data_from_url(self, url: str) -> str:
        return requests.get(url, allow_redirects=True).text


class Parameters:
    __DATASET_KEY_CHARACTER = "$"
    __DATASET_WITH_OBJECT_KEY_CHARACTER = "."
    __REMOVE_KEY_CHARACTER = ""

    def __init__(self, database: Database, data: Data):
        self.__database_connector = database
        self.__data = data

    def treat(self, method_parameters: dict) -> dict:
        parameters = method_parameters.copy()

        for name, value in parameters.items():
            if self.__is_dataset(value):
                dataset_name = self.__get_dataset_name_from_value(
                    value)
                if self.__has_dot_in_dataset_name(value):
                    object_name = self.__get_name_after_dot_from_value(value)

                    parameters[name] = self.__data.get_object_from_dataset(
                        dataset_name, object_name)

                else:
                    parameters[name] = self.__data.get_dataset_content(
                        dataset_name)

        return parameters

    def __is_dataset(self, value: str) -> bool:
        return self.__DATASET_KEY_CHARACTER in value

    def __get_dataset_name_from_value(self, value: str) -> str:
        dataset_name = value.replace(self.__DATASET_KEY_CHARACTER,
                                     self.__REMOVE_KEY_CHARACTER)
        return dataset_name.split(self.__DATASET_WITH_OBJECT_KEY_CHARACTER)[
            FIRST_ARGUMENT]

    def __has_dot_in_dataset_name(self, dataset_name: str) -> bool:
        return self.__DATASET_WITH_OBJECT_KEY_CHARACTER in dataset_name

    def __get_name_after_dot_from_value(self, value: str) -> str:
        return value.split(
            self.__DATASET_WITH_OBJECT_KEY_CHARACTER)[SECOND_ARGUMENT]


class Execution:
    def __init__(self,
                 database_connector: Database,
                 filename: str,
                 service_type: str,
                 storage: ObjectStorage,
                 metadata_creator: Metadata,
                 parameters_handler: Parameters,
                 function_handler: Function
                 ):
        self.__metadata_creator = metadata_creator
        self.__thread_pool = ThreadPoolExecutor()
        self.__database_connector = database_connector
        self.__storage = storage
        self.__parameters_handler = parameters_handler
        self.__function_handler = function_handler
        self.filename = filename
        self.service_type = service_type

    def create(self,
               function: str,
               function_parameters: dict,
               description: str) -> None:
        self.__metadata_creator.create_file(self.filename, self.service_type)

        self.__thread_pool.submit(self.__pipeline,
                                  function,
                                  function_parameters,
                                  description)

    def update(self,
               function: str,
               function_parameters: dict,
               description: str) -> None:
        self.__metadata_creator.update_finished_flag(self.filename, False)

        self.__thread_pool.submit(self.__pipeline,
                                  function,
                                  function_parameters,
                                  description)

    def __pipeline(self,
                   function: str,
                   function_parameters: dict,
                   description: str) -> None:
        function_result, function_message, function_error = \
            self.__execute_function(
                function,
                function_parameters)

        if function_result and not function_error:
            self.__storage.save(function_result, self.filename)
            self.__metadata_creator.update_finished_flag(self.filename,
                                                         flag=True)

        self.__metadata_creator.create_execution_document(self.filename,
                                                          description,
                                                          function_parameters,
                                                          function_message,
                                                          function_error)

    def __execute_function(self, function: str,
                           parameters: dict) -> (dict, str, str):
        function_parameters = self.__parameters_handler.treat(parameters)
        function_code = self.__function_handler.treat(function)

        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()

        function_response = None
        function_error = None
        context_variables = locals()

        try:
            exec(function_code, function_parameters, context_variables)
        except Exception as error:
            function_message = redirected_output.getvalue()
            sys.stdout = old_stdout
            function_error = repr(error)
            return function_response, function_message, function_error

        function_message = redirected_output.getvalue()
        sys.stdout = old_stdout

        return function_response, function_message, function_error
