from pyspark.sql import SparkSession
import os

SPARKMASTER_HOST = "SPARKMASTER_HOST"
SPARKMASTER_PORT = "SPARKMASTER_PORT"


class ProcessorInterface():
    def projection(self, fields):
        pass


class SparkManager(ProcessorInterface):
    MESSAGE_CREATED_FILE = "file_created"

    def __init__(self, database_url_input, database_url_output):
        self.spark_session = SparkSession \
                            .builder \
                            .appName("projection") \
                            .config("spark.mongodb.input.uri",
                                    database_url_input) \
                            .config("spark.mongodb.output.uri",
                                    database_url_output) \
                            .config('spark.jars.packages',
                                    'org.mongodb.spark:mongo-spark' +
                                    '-connector_2.11:2.4.2')\
                            .master("spark://" +
                                    os.environ[SPARKMASTER_HOST] +
                                    ':' + str(os.environ[SPARKMASTER_PORT])) \
                            .getOrCreate()

    def projection(self, fields):
        data_frame = self.spark_session.read.format(
                "com.mongodb.spark.sql.DefaultSource").load()

        data_frame.printSchema()

        projection_data_frame = data_frame.select(*fields).collect()

        projection_data_frame.write.format(
                "com.mongodb.spark.sql.DefaultSource").save()
