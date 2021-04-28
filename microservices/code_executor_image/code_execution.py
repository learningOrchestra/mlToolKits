from concurrent.futures import ThreadPoolExecutor
from utils import Database, Data, ObjectStorage, Metadata
from constants import Constants
from io import StringIO
import sys
import validators
import requests
import traceback


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
    __CLASS_INSTANCE_CHARACTER = "#"
    __DATASET_WITH_OBJECT_KEY_CHARACTER = "."
    __REMOVE_KEY_CHARACTER = ""

    def __init__(self, database: Database, data: Data):
        self.__database_connector = database
        self.__data = data

    def treat(self, method_parameters: dict) -> dict:
        parameters = method_parameters.copy()

        for name, value in parameters.items():
            if type(value) is list:
                new_value = []
                for item in value:
                    new_value.append(self.__treat_value(item))
                parameters[name] = new_value
            else:
                parameters[name] = self.__treat_value(value)

        return parameters

    def __treat_value(self, value: object) -> object:
        if self.__is_dataset(value):
            dataset_name = self.__get_dataset_name_from_value(
                value)

            if self.__has_dot_in_dataset_name(value):
                object_name = self.__get_name_after_dot_from_value(value)
                return self.__data.get_object_from_dataset(
                    dataset_name, object_name)

            else:
                return self.__data.get_dataset_content(
                    dataset_name)

        elif self.__is_a_class_instance(value):
            return self.__get_a_class_instance(value)

        else:
            return value

    def __get_a_class_instance(self, class_code: str) -> object:
        import tensorflow
        class_instance_name = "class_instance"
        class_instance = None
        context_variables = {}

        class_code = class_code.replace(
            self.__CLASS_INSTANCE_CHARACTER,
            f'{class_instance_name}=')

        exec(class_code, locals(), context_variables)

        return context_variables[class_instance_name]

    def __is_a_class_instance(self, value: object) -> bool:
        if type(value) != str:
            return False
        else:
            return self.__CLASS_INSTANCE_CHARACTER in value

    def __is_dataset(self, value: object) -> bool:
        if type(value) != str:
            return False
        else:
            return self.__DATASET_KEY_CHARACTER in value

    def __get_dataset_name_from_value(self, value: str) -> str:
        dataset_name = value.replace(self.__DATASET_KEY_CHARACTER,
                                     self.__REMOVE_KEY_CHARACTER)
        return dataset_name.split(self.__DATASET_WITH_OBJECT_KEY_CHARACTER)[
            Constants.FIRST_ARGUMENT]

    def __has_dot_in_dataset_name(self, dataset_name: str) -> bool:
        return self.__DATASET_WITH_OBJECT_KEY_CHARACTER in dataset_name

    def __get_name_after_dot_from_value(self, value: str) -> str:
        return value.split(
            self.__DATASET_WITH_OBJECT_KEY_CHARACTER)[Constants.SECOND_ARGUMENT]


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

        if function_error is None:
            self.__storage.save(function_result, self.filename)
            self.__metadata_creator.update_finished_flag(self.filename,
                                                         flag=True)

        self.__metadata_creator.create_execution_document(self.filename,
                                                          description,
                                                          function_parameters,
                                                          function_message,
                                                          function_error)

    def __execute_function(self, function: str,
                           parameters: dict) -> (object, str, str):
        # This function returns a tuple with 3 items, the first item is a dict
        # defined inside of executed function, the second item is the the output
        # caught in executed function and the last item is the the exception
        # message, in case of a threw exception in executed function.

        function_parameters = self.__parameters_handler.treat(parameters)
        function_code = self.__function_handler.treat(function)

        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()

        context_variables = {}

        try:
            exec(function_code, function_parameters, context_variables)
            function_message = redirected_output.getvalue()
            sys.stdout = old_stdout

            return context_variables["response"], function_message, None

        except Exception as error:
            traceback.print_exc()
            function_message = redirected_output.getvalue()
            sys.stdout = old_stdout
            function_error = repr(error)
            return None, function_message, function_error
