from concurrent.futures import ThreadPoolExecutor


class DataType:
    METADATA_DOCUMENT_ID = 0
    DOCUMENT_ID_NAME = "_id"
    STRING_TYPE = "string"
    NUMBER_TYPE = "number"

    def __init__(self, database_connector, metadata_handler):
        self.database_connector = database_connector
        self.thread_pool = ThreadPoolExecutor()
        self.metadata_handler = metadata_handler

    def field_converter(self, filename, field, field_type):
        query = {}
        for document in self.database_connector.find(filename, query):
            if document[self.DOCUMENT_ID_NAME] == self.METADATA_DOCUMENT_ID:
                continue

            values = {}
            if field_type == self.STRING_TYPE:
                if document[field] == str:
                    continue
                if document[field] is None:
                    values[field] = ""
                else:
                    values[field] = str(document[field])

            elif field_type == self.NUMBER_TYPE:
                if (
                        document[field] == int
                        or document[field] == float
                        or document[field] is None
                ):
                    continue
                if document[field] == "":
                    values[field] = None
                else:
                    values[field] = float(document[field])

                    if values[field].is_integer():
                        values[field] = int(values[field])

            self.database_connector.update_one(filename, values, document)

    def convert_existent_file(self, filename, fields_dictionary):

        self.metadata_handler.update_finished_flag(filename, False)

        self.thread_pool.submit(self.field_file_converter, filename,
                                fields_dictionary)

    def field_file_converter(self, filename, fields_dictionary):
        for field in fields_dictionary:
            self.field_converter(filename, field,
                                 fields_dictionary[field])

        self.metadata_handler.update_finished_flag(filename, True)
