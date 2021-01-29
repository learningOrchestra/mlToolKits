import importlib
from concurrent.futures import ThreadPoolExecutor
from utils import Metadata, Database, ModelStorage
from constants import *


class DefaultModel:
    def __init__(self,
                 database_connector: Database,
                 model_name: str,
                 metadata_creator: Metadata,
                 module_path: str,
                 class_name: str,
                 storage: ModelStorage):
        self.__metadata_creator = metadata_creator
        self.__thread_pool = ThreadPoolExecutor()
        self.__database_connector = database_connector
        self.__storage = storage
        self.model_name = model_name
        self.module_path = module_path
        self.class_name = class_name

    def create(self,
               description: str,
               class_parameters: dict) -> None:
        self.__metadata_creator.create_file(self.model_name, self.module_path,
                                            self.class_name)
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
        try:
            module = importlib.import_module(self.module_path)
            module_function = getattr(module, self.class_name)
            function_instance = module_function(**class_parameters)
            self.__storage.save(self.model_name, function_instance)
            self.__metadata_creator.update_finished_flag(self.model_name,
                                                         flag=True)
        except Exception as exception:
            self.__metadata_creator.create_model_document(self.model_name,
                                                          description,
                                                          class_parameters,
                                                          str(exception))
            return

        self.__metadata_creator.create_model_document(self.model_name,
                                                      description,
                                                      class_parameters)
