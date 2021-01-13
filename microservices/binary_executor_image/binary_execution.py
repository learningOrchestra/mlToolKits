import importlib
import pickle
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from utils import *
from constants import *
import os


class Execution:
    __WRITE_MODEL_OBJECT_OPTION = "wb"
    __READ_MODEL_OBJECT_OPTION = "rb"
    __DATASET_KEY_CHARACTER = "$"
    __REMOVE_KEY_CHARACTER = ""

    def __init__(self, metadata_creator: Metadata,
                 database_connector: Database,
                 executor_name: str,
                 parent_name: str,
                 class_method: str,
                 service_type: str):
        self.__metadata_creator = metadata_creator
        self.__thread_pool = ThreadPoolExecutor()
        self.__database_connector = database_connector
        self.executor_name = executor_name
        self.parent_name = parent_name
        self.class_method = class_method
        self.service_type = service_type
        self.__metadata_creator.create_file(parent_name, executor_name,
                                            class_method, service_type)

    def execute(self,
                module_path: str,
                method_parameters: dict,
                description: str) -> None:

        self.__thread_pool.submit(self.__pipeline,
                                  module_path,
                                  method_parameters,
                                  description)

    def update(self,
               module_path: str,
               method_parameters: dict,
               description: str) -> None:
        self.__metadata_creator.update_finished_flag(self.executor_name, False)

        self.__thread_pool.submit(self.__pipeline,
                                  module_path,
                                  method_parameters,
                                  description)

    def __read_a_model_instance(self) -> object:
        model_binary_instance = open(self.__get_read_binary_path(),
                                     self.__READ_MODEL_OBJECT_OPTION)
        return pickle.load(model_binary_instance)

    def __pipeline(self,
                   module_path: str,
                   method_parameters: dict,
                   description: str) -> None:
        try:
            importlib.import_module(module_path)
            model_instance = self.__read_a_model_instance()
            method_result = self.__execute_a_object_method(model_instance,
                                                           self.class_method,
                                                           method_parameters)
            self.__save(method_result)
            self.__metadata_creator.update_finished_flag(self.executor_name,
                                                         flag=True)

        except Exception as exception:
            self.__metadata_creator.create_execution_document(
                self.executor_name,
                description,
                method_parameters,
                exception.args[
                    FIRST_ARGUMENT])
            return None

        self.__metadata_creator.create_execution_document(self.executor_name,
                                                          description,
                                                          method_parameters,
                                                          )

    def __parameters_treatment(self, method_parameters: dict) -> dict:
        for name, value in method_parameters.items():
            if self.__DATASET_KEY_CHARACTER in value:
                dataset_name = value.replace(self.__DATASET_KEY_CHARACTER,
                                             self.__REMOVE_KEY_CHARACTER)
                dataset = self.__database_connector.get_entire_collection(
                    dataset_name)

                dataset_dataframe = pd.DataFrame(dataset)
                method_parameters[name] = dataset_dataframe.values

        return method_parameters

    def __execute_a_object_method(self, class_instance: object, method: str,
                                  parameters: dict) -> object:
        model_method = getattr(class_instance, method)

        return model_method(**self.__parameters_treatment(parameters))

    def __save(self, model_instance: object) -> None:
        model_output = open(self.__get_write_binary_path(),
                            self.__WRITE_MODEL_OBJECT_OPTION)
        pickle.dump(model_instance, model_output)
        model_output.close()

    def __get_read_binary_path(self):
        metadata_document = self.__metadata_creator.read_metadata(
            self.parent_name)
        parent_file_type = metadata_document[TYPE_FIELD_NAME]

        if parent_file_type == DEFAULT_MODEL_MICROSERVICE_TYPE:
            return os.environ[MODELS_VOLUME_PATH] + "/" + self.parent_name
        else:
            return os.environ[BINARY_VOLUME_PATH] + "/" + \
                   parent_file_type + "/" + self.parent_name

    def __get_write_binary_path(self):
        return os.environ[BINARY_VOLUME_PATH] + "/" + \
               self.service_type + "/" + self.executor_name
