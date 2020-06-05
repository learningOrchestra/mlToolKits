from pyspark.sql import SparkSession
import os

SPARKMASTER_HOST = "SPARKMASTER_HOST"
SPARKMASTER_PORT = "SPARKMASTER_PORT"


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
                            .master("spark://" +
                                    os.environ[SPARKMASTER_HOST] +
                                    ':' + str(os.environ[SPARKMASTER_PORT])) \
                            .getOrCreate()

    def projection(self, fields):
        data_frame = self.spark_session.read.format(
                "com.mongodb.spark.sql.DefaultSource").load()

        projection_data_frame = data_frame.select(fields).collect()

        projection_data_frame.write.format(
                "com.mongodb.spark.sql.DefaultSource").save()
