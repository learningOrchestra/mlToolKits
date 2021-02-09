from concurrent.futures import ThreadPoolExecutor
from utils import *
from constants import *


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
                 parameters_handler: Parameters
                 ):
        self.__metadata_creator = metadata_creator
        self.__thread_pool = ThreadPoolExecutor()
        self.__database_connector = database_connector
        self.__storage = storage
        self.__parameters_handler = parameters_handler
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

        '''self.__thread_pool.submit(self.__pipeline,
                                  function,
                                  function_parameters,
                                  description)'''
        self.__pipeline(
            function,
            function_parameters,
            description)

    def __pipeline(self,
                   function: str,
                   function_parameters: dict,
                   description: str) -> None:
        # try:
        function_result = self.__execute_function(function,
                                                  function_parameters)

        self.__storage.save(function_result, self.filename)

        self.__metadata_creator.update_finished_flag(self.filename,
                                                     flag=True)

        '''except Exception as exception:
            self.__metadata_creator.create_execution_document(
                self.filename,
                description,
                function_parameters,
                str(exception))
            return None'''

        self.__metadata_creator.create_execution_document(self.filename,
                                                          description,
                                                          function_parameters,
                                                          )

    def __execute_function(self, function: str,
                           parameters: dict) -> dict:
        function_parameters = self.__parameters_handler.treat(parameters)
        context_variables = locals()
        exec(function, globals(), context_variables)

        return context_variables["response"]
