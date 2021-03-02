from concurrent.futures import ThreadPoolExecutor
from utils import Database, ExecutionStorage, Metadata, Data
import importlib
from constants import Constants


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

    def __treat_value(self, value: str) -> object:
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

    def __get_a_class_instance(self, class_code: str) -> object:
        class_instance_name = "class_instance"
        class_instance = None
        context_variables = {}

        class_code = class_code.replace(
            self.__CLASS_INSTANCE_CHARACTER,
            f'{class_instance_name}=')

        import tensorflow
        exec(class_code, locals(), context_variables)

        return context_variables[class_instance_name]

    def __is_a_class_instance(self, value: str) -> bool:
        return self.__CLASS_INSTANCE_CHARACTER in value

    def __is_dataset(self, value: str) -> bool:
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
                 storage: ExecutionStorage,
                 metadata_creator: Metadata,
                 module_path: str,
                 class_name: str,
                 class_parameters: dict,
                 parameters_handler: Parameters
                 ):
        self.__metadata_creator = metadata_creator
        self.__thread_pool = ThreadPoolExecutor()
        self.__database_connector = database_connector
        self.__storage = storage
        self.__parameters_handler = parameters_handler
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
                repr(exception))
            return None

        self.__metadata_creator.create_execution_document(self.filename,
                                                          description,
                                                          class_method_name,
                                                          method_parameters
                                                          )

    def __execute_a_object_method(self, class_instance: object, method: str,
                                  parameters: dict) -> object:
        method_reference = getattr(class_instance, method)
        treated_parameters = self.__parameters_handler.treat(parameters)
        return method_reference(**treated_parameters)
