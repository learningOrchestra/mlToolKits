import importlib
import pickle
from concurrent.futures import ThreadPoolExecutor
from default_model_utils import Metadata


class DefaultModel:
    WRITE_MODEL_OBJECT_OPTION = "wb"
    READ_MODEL_OBJECT_OPTION = "rb"

    def __init__(self, metadata_creator: Metadata):
        self.metadata_creator = metadata_creator
        self.thread_pool = ThreadPoolExecutor()

    def create(self, model_name: str, tool: str, function: str,
               description: str,
               function_parameters: dict):
        self.metadata_creator.create_file(model_name, description, tool,
                                          function, function_parameters)

        self.thread_pool.submit(self.__pipeline, model_name, tool, function,
                                function_parameters)

    def update(self, model_name: str, tool: str, function: str,
               description: str,
               function_parameters: dict):
        # TODO create update method
        pass

    def __pipeline(self, model_name: str, tool: str, function: str,
                   function_parameters: dict):
        module = importlib.import_module(tool)
        module_function = getattr(module, function)
        function_instance = module_function(*function_parameters)
        self.__save(function_instance, model_name)
        self.metadata_creator.update_finished_flag(model_name, flag=True)

    def __save(self, model_instance, model_name: str):
        model_output = open(model_name, self.WRITE_MODEL_OBJECT_OPTION)
        pickle.dumps(model_instance, model_output)
        model_output.close()

    @staticmethod
    def available_tools() -> list:
        available_tools = ["sklearn"]
        return available_tools
