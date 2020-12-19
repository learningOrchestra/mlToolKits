import importlib
import pickle
from concurrent.futures import ThreadPoolExecutor


class DefaultModel:
    WRITE_MODEL_OBJECT_OPTION = "wb"

    def __init__(self, metadata_creator):
        self.metadata_creator = metadata_creator
        self.thread_pool = ThreadPoolExecutor()

    def create(self, model_name, tool, function, description,
               function_parameters):
        self.metadata_creator.create_file(model_name, description, tool,
                                          function, function_parameters)

        self.thread_pool.submit(self.__pipeline, model_name, tool, function,
                                function_parameters)

    def __pipeline(self, model_name, tool, function, function_parameters):
        module = importlib.import_module(tool)
        module_function = getattr(module, function)
        function_instance = module_function(*function_parameters)
        self.__save(function_instance, model_name)
        self.metadata_creator.update_finished_flag(model_name, flag=True)

    def __save(self, model_nstance, model_name):
        model_output = open(model_name, self.WRITE_MODEL_OBJECT_OPTION)
        pickle.dumps(model_nstance, model_output)
        model_output.close()
