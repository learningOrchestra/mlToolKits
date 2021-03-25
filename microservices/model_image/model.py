import importlib
from concurrent.futures import ThreadPoolExecutor
from utils import Metadata, Database, ObjectStorage, Data
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


class Model:
    def __init__(self,
                 database_connector: Database,
                 parameters_handler: Parameters,
                 model_name: str,
                 service_type: str,
                 metadata_creator: Metadata,
                 module_path: str,
                 class_name: str,
                 storage: ObjectStorage):
        self.__metadata_creator = metadata_creator
        self.__parameters_handler = parameters_handler
        self.__thread_pool = ThreadPoolExecutor()
        self.__database_connector = database_connector
        self.__storage = storage
        self.service_type = service_type
        self.model_name = model_name
        self.module_path = module_path
        self.class_name = class_name

    def create(self,
               description: str,
               class_parameters: dict) -> None:
        self.__metadata_creator.create_file(self.model_name,
                                            self.service_type,
                                            self.module_path,
                                            self.class_name)
        '''self.__thread_pool.submit(self.__pipeline,
                                  class_parameters,
                                  description)'''
        self.__thread_pool.submit(self.__pipeline,
                                  class_parameters,
                                  description)

    def update(self,
               description: str,
               class_parameters: dict) -> None:
        self.__metadata_creator.update_finished_flag(self.model_name, False)

        self.__thread_pool.submit(self.__pipeline,
                                  class_parameters,
                                  description)

    def __pipeline(self,
                   class_parameters: dict, description: str) -> None:
        #try:
        module = importlib.import_module(self.module_path)
        class_reference = getattr(module, self.class_name)
        class_instance = self.__create_a_class_instance(class_reference,
                                                        class_parameters)
        self.__storage.save(self.model_name, class_instance)
        self.__metadata_creator.update_finished_flag(self.model_name,
                                                     flag=True)
        '''except Exception as exception:
            self.__metadata_creator.create_model_document(self.model_name,
                                                          description,
                                                          class_parameters,
                                                          repr(exception))
            return'''

        self.__metadata_creator.create_model_document(self.model_name,
                                                      description,
                                                      class_parameters)

    def __create_a_class_instance(self,
                                  class_reference,
                                  class_parameters: dict) -> object:
        treated_parameters = self.__parameters_handler.treat(class_parameters)
        return class_reference(**treated_parameters)
