from concurrent.futures import ThreadPoolExecutor


class Histogram:
    METADATA_DOCUMENT_ID = 0
    DOCUMENT_ID_NAME = "_id"

    def __init__(self, database_connector, metadata_handler):
        self.database_connector = database_connector
        self.metadata_handler = metadata_handler
        self.thread_pool = ThreadPoolExecutor()

    def create_file(self, parent_filename, histogram_filename, fields):
        self.metadata_handler.create_file(
            parent_filename,
            histogram_filename,
            fields)

        self.thread_pool.submit(
            self.file_processing,
            parent_filename,
            histogram_filename,
            fields)

    def file_processing(self, parent_filename, histogram_filename, fields):
        document_id = 1

        for field in fields:
            field_accumulator = "$" + field
            print(field_accumulator, flush=True)
            pipeline = [
                {"$group": {"_id": field_accumulator, "count": {"$sum": 1}}}]

            field_result = {
                field: self.database_connector.aggregate(parent_filename,
                                                         pipeline),
                self.DOCUMENT_ID_NAME: document_id,
            }
            document_id += 1

            self.database_connector.insert_one_in_file(histogram_filename,
                                                       field_result)

        self.metadata_handler.update_finish_flag(histogram_filename, True)
