import importlib
import pickle
from concurrent.futures import ThreadPoolExecutor
from utils import Metadata, Database


class DefaultModel:
    __WRITE_MODEL_OBJECT_OPTION = "wb"
    __READ_MODEL_OBJECT_OPTION = "rb"

    def __init__(self, metadata_creator: Metadata,
                 database_connector: Database):
        self.__metadata_creator = metadata_creator
        self.__thread_pool = ThreadPoolExecutor()
        self.__database_connector = database_connector

    def create(self, model_name: str, tool: str, function: str,
               description: str,
               function_parameters: dict):
        self.__metadata_creator.create_file(model_name, tool,
                                            function)

        self.__create_model_document(model_name, description,
                                     function_parameters)

        self.__thread_pool.submit(self.__pipeline, model_name, tool, function,
                                  function_parameters)

    def update(self, model_name: str, tool: str, function: str,
               description: str,
               function_parameters: dict):
        self.__metadata_creator.update_finished_flag(model_name, False)

        self.__create_model_document(model_name, description,
                                     function_parameters)

        self.__thread_pool.submit(self.__pipeline, model_name, tool, function,
                                  function_parameters)

    @staticmethod
    def available_tools() -> list:
        available_tools = ["sklearn"]
        return available_tools

    def __create_model_document(self, model_name, description,
                                function_parameters):
        model_document = {
            "description": description,
            "functionParameters": function_parameters
        }
        self.__database_connector.insert_one_in_file(model_name, model_document)

    def __pipeline(self, model_name: str, tool: str, function: str,
                   function_parameters: dict):
        module = importlib.import_module(tool)
        module_function = getattr(module, function)
        function_instance = module_function(*function_parameters)
        self.__save(function_instance, model_name)
        self.__metadata_creator.update_finished_flag(model_name, flag=True)

    def __save(self, model_instance, model_name: str):
        model_output = open(model_name, self.__WRITE_MODEL_OBJECT_OPTION)
        pickle.dumps(model_instance, model_output)
        model_output.close()
