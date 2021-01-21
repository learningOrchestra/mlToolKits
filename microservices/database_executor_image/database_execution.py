import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from utils import *
from constants import *
import os
import seaborn as sns


class ExecutionStorage:
    def save(self, instance: pd.DataFrame, filename: str) -> None:
        pass

    def delete(self, filename: str):
        pass


class DatabaseStorage(ExecutionStorage):
    def __init__(self, database_connector: Database):
        self.__database_connector = database_connector
        self.__thread_pool = ThreadPoolExecutor()

    def save(self, instance: pd.DataFrame, filename: str) -> None:
        instance_dict = instance.to_dict("records")
        self.__database_connector.delete_data_in_file(filename)
        self.__database_connector.insert_many_in_file(filename,
                                                      instance_dict)

    def delete(self, filename: str):
        self.__thread_pool.submit(
            self.__database_connector.delete_file, filename)


class VolumeStorage(ExecutionStorage):
    def __init__(self, database_connector: Database = None):
        self.__database_connector = database_connector
        self.__thread_pool = ThreadPoolExecutor()

    def save(self, instance: pd.DataFrame, filename: str) -> None:
        output_path = self.get_image_path(filename)
        sns_plot = sns.scatterplot(data=instance)
        sns_plot.get_figure().savefig(output_path)

    def delete(self, filename: str):
        self.__thread_pool.submit(
            self.__database_connector.delete_file, filename)
        self.__thread_pool.submit(os.remove,
                                  VolumeStorage.get_image_path(filename))

    @staticmethod
    def get_image_path(filename: str) -> str:
        return os.environ[IMAGES_VOLUME_PATH] + "/" + filename

    @staticmethod
    def get_images_path() -> str:
        return os.environ[IMAGES_VOLUME_PATH] + "/"


class Execution:
    __WRITE_MODEL_OBJECT_OPTION = "wb"
    __READ_MODEL_OBJECT_OPTION = "rb"
    __DATASET_KEY_CHARACTER = "$"
    __REMOVE_KEY_CHARACTER = ""

    def __init__(self,
                 database_connector: Database,
                 filename: str,
                 service_type: str,
                 storage: ExecutionStorage,
                 metadata_creator: Metadata = None,
                 module_path: str = None,
                 class_name: str = None,
                 class_parameters: dict = None
                 ):
        self.__metadata_creator = metadata_creator
        self.__thread_pool = ThreadPoolExecutor()
        self.__database_connector = database_connector
        self.__storage = storage
        self.filename = filename
        self.module_path = module_path
        self.class_name = class_name
        self.class_parameters = class_parameters
        self.service_type = service_type

    def create(self,
               class_method_name: str,
               method_parameters: dict,
               description: str) -> None:

        self.__metadata_creator.create_file(self.filename,
                                            self.module_path,
                                            self.class_name,
                                            self.class_parameters,
                                            self.service_type)

        self.__thread_pool.submit(self.__pipeline,
                                  self.module_path,
                                  self.class_name,
                                  self.class_parameters,
                                  class_method_name,
                                  method_parameters,
                                  description)

    def update(self,
               class_method_name: str,
               method_parameters: dict,
               description: str) -> None:
        self.__metadata_creator.update_finished_flag(self.filename, False)

        self.__thread_pool.submit(self.__pipeline,
                                  self.module_path,
                                  self.class_name,
                                  self.class_parameters,
                                  class_method_name,
                                  method_parameters,
                                  description)

    def __pipeline(self,
                   module_path: str,
                   class_name: str,
                   class_parameters: dict,
                   class_method_name: str,
                   method_parameters: dict,
                   description: str) -> None:
        try:
            module = importlib.import_module(module_path)
            module_function = getattr(module, class_name)
            class_instance = module_function(**class_parameters)

            method_result = self.__execute_a_object_method(class_instance,
                                                           class_method_name,
                                                           method_parameters)

            self.__storage.save(method_result, self.filename)

            self.__metadata_creator.update_finished_flag(self.filename,
                                                         flag=True)

        except Exception as exception:
            self.__metadata_creator.create_execution_document(
                self.filename,
                description,
                class_method_name,
                method_parameters,
                str(exception))
            return None

        self.__metadata_creator.create_execution_document(self.filename,
                                                          description,
                                                          class_method_name,
                                                          method_parameters
                                                          )

    def __parameters_treatment(self, method_parameters: dict) -> dict:
        parameters = method_parameters.copy()
        for name, value in parameters.items():
            if self.__DATASET_KEY_CHARACTER in value:
                dataset_name = value.replace(self.__DATASET_KEY_CHARACTER,
                                             self.__REMOVE_KEY_CHARACTER)
                dataset = self.__database_connector.get_entire_collection(
                    dataset_name)

                dataset_dataframe = pd.DataFrame(dataset)
                parameters[name] = dataset_dataframe.values

        return parameters

    def __execute_a_object_method(self, class_instance: object, method: str,
                                  parameters: dict) -> pd.DataFrame:
        model_method = getattr(class_instance, method)
        method_result = model_method(**self.__parameters_treatment(parameters))
        return pd.DataFrame(method_result)
