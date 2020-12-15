import sklearn

class DefaultModel():
    def __init__(self, metadata_creator):
        self.metadata_creator = metadata_creator

    def create(self, model_name, tool, function, description, function_parameters):
        pass

    def update(self):
        pass
