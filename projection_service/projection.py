from pyspark.sql import SparkSession


class ProcessorInterface():
    def projection(self, fields):
        pass


class SparkManager(ProcessorInterface):
    MESSAGE_CREATED_FILE = "file_created"

    def __init__(self, database_url, database_name, filename_input,
                 filename_output):
        self.spark_session = SparkSession \
                            .builder \
                            .appName("projection") \
                            .config("spark.mongodb.input.uri",
                                    database_url +
                                    database_name + '.' +
                                    filename_input) \
                            .config("spark.mongodb.output.uri",
                                    database_url +
                                    database_name + '.' +
                                    filename_output) \
                            .getOrCreate()

    def projection(self, fields):
        data_frame = self.spark_session.read.format("mongo").load()
        projection_data_frame = data_frame.select(fields).collect()
        projection_data_frame.write.format("mongo").save()
