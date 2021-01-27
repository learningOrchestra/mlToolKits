from concurrent.futures import ThreadPoolExecutor
from utils import *
from constants import *
import os
import seaborn as sns
import pickle


class ExecutionStorage:
    def save(self, instance: pd.DataFrame, filename: str) -> None:
        pass

    def delete(self, filename: str) -> None:
        pass


class DatabaseStorage(ExecutionStorage):
    __WRITE_OBJECT_OPTION = "wb"

    def __init__(self, database_connector: Database):
        self.__database_connector = database_connector
        self.__thread_pool = ThreadPoolExecutor()

    def save(self, instance: pd.DataFrame, filename: str) -> None:
        output_path = self.__get_instance_binary_path(filename)

        instance_output = open(output_path,
                               self.__WRITE_OBJECT_OPTION)
        pickle.dump(instance, instance_output)
        instance_output.close()

    def delete(self, filename: str) -> None:
        self.__thread_pool.submit(
            self.__database_connector.delete_file, filename)
        self.__thread_pool.submit(
            os.remove, self.__get_instance_binary_path(filename))

    def __get_instance_binary_path(self, filename: str) -> str:
        return os.environ[TRANSFORM_VOLUME_PATH] + "/" + filename


class VolumeStorage(ExecutionStorage):
    def __init__(self, database_connector: Database = None):
        self.__database_connector = database_connector
        self.__thread_pool = ThreadPoolExecutor()

    def save(self, instance: pd.DataFrame, filename: str) -> None:
        output_path = self.get_image_path(filename)
        sns_plot = sns.scatterplot(data=instance)
        sns_plot.get_figure().savefig(output_path)

    def delete(self, filename: str) -> None:
        self.__thread_pool.submit(
            self.__database_connector.delete_file, filename)
        self.__thread_pool.submit(os.remove,
                                  VolumeStorage.get_image_path(filename))

    @staticmethod
    def get_image_path(filename: str) -> str:
        return os.environ[IMAGES_VOLUME_PATH] + "/" + filename + IMAGE_FORMAT


class Execution:
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

        '''self.__thread_pool.submit(self.__pipeline,
                                  self.module_path,
                                  self.class_name,
                                  self.class_parameters,
                                  class_method_name,
                                  method_parameters,
                                  description)'''
        print("teste0", flush=True)
        self.__pipeline(
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

            print("teste1", flush=True)

            method_result = self.__execute_a_object_method(class_instance,
                                                           class_method_name,
                                                           method_parameters)

            print("teste2", flush=True)

            self.__storage.save(method_result, self.filename)

            print("teste3", flush=True)

            self.__metadata_creator.update_finished_flag(self.filename,
                                                         flag=True)

        except Exception as exception:
            print("teste4", flush=True)

            self.__metadata_creator.create_execution_document(
                self.filename,
                description,
                class_method_name,
                method_parameters,
                str(exception))
            return None

        print("teste5", flush=True)

        self.__metadata_creator.create_execution_document(self.filename,
                                                          description,
                                                          class_method_name,
                                                          method_parameters
                                                          )

    def __execute_a_object_method(self, class_instance: object, method: str,
                                  parameters: dict) -> pd.DataFrame:
        model_method = getattr(class_instance, method)
        method_result = model_method(**parameters)
        return pd.DataFrame(method_result)


class Parameters:
    __DATASET_KEY_CHARACTER = "$"
    __DATASET_COLUMN_KEY_CHARACTER = "."
    __REMOVE_KEY_CHARACTER = ""

    def __init__(self, database: Database):
        self.__database_connector = database

    def treat(self, method_parameters: dict) -> dict:
        parameters = method_parameters.copy()

        for name, value in parameters.items():
            if self.__is_dataset(value):
                dataset_name = self.__get_dataset_name_from_value(
                    value)
                print(dataset_name, flush=True)
                data = Data(self.__database_connector, dataset_name)

                if self.__has_column_in_dataset_name(value):
                    column_name = self.__get_column_name_from_value(value)
                    print(column_name, flush=True)

                    parameters[name] = data.get_filename_column_content(
                        column_name)

                    print(parameters[name], flush=True)
                else:
                    parameters[name] = data.get_filename_content()
                    print(parameters[name], flush=True)


        return parameters

    def __is_dataset(self, value: str) -> bool:
        return self.__DATASET_KEY_CHARACTER in value

    def __get_dataset_name_from_value(self, value: str) -> str:
        dataset_name = value.replace(self.__DATASET_KEY_CHARACTER,
                                     self.__REMOVE_KEY_CHARACTER)
        return dataset_name.split(self.__DATASET_COLUMN_KEY_CHARACTER)[
            FIRST_ARGUMENT]

    def __has_column_in_dataset_name(self, dataset_name: str) -> bool:
        return self.__DATASET_COLUMN_KEY_CHARACTER in dataset_name

    def __get_column_name_from_value(self, value: str) -> str:
        return value.split(
            self.__DATASET_COLUMN_KEY_CHARACTER)[SECOND_ARGUMENT]
