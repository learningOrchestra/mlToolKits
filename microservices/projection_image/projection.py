from pyspark.sql import SparkSession
import os
from concurrent.futures import ThreadPoolExecutor

SPARKMASTER_HOST = "SPARKMASTER_HOST"
SPARKMASTER_PORT = "SPARKMASTER_PORT"
SPARK_DRIVER_PORT = "SPARK_DRIVER_PORT"
PROJECTION_HOST_NAME = "PROJECTION_HOST_NAME"


class Projection:
    FINISHED = "finished"
    DOCUMENT_ID = "_id"
    MONGO_SPARK_SOURCE = "com.mongodb.spark.sql.DefaultSource"
    METADATA_FILE_ID = 0
    database_url_output = None
    MAX_NUMBER_THREADS = 3

    def __init__(self, metadata_creator, database_url_input,
                 database_url_output):
        self.database_url_input = database_url_input
        self.database_url_output = database_url_output
        self.metadata_creator = metadata_creator
        self.thread_pool = ThreadPoolExecutor()

    def create(self, parent_filename, projection_filename, fields):
        self.metadata_creator.create_file(
            projection_filename,
            parent_filename,
            fields)

        self.thread_pool.submit(self.execute_spark_job,
                                projection_filename, fields)

    def execute_spark_job(self, projection_filename, fields):
        spark_session = (
            SparkSession
                .builder
                .config("spark.mongodb.input.uri", self.database_url_input)
                .config("spark.mongodb.output.uri", self.database_url_output)
                .config("spark.driver.port", os.environ[SPARK_DRIVER_PORT])
                .config("spark.driver.host", os.environ[PROJECTION_HOST_NAME])
                .config("spark.scheduler.mode", "FAIR")
                .config("spark.jars.packages",
                        "org.mongodb.spark:mongo-spark-connector_2.11:2.4.2",
                        )
                .master(
                f'spark://{os.environ[SPARKMASTER_HOST]}:'
                f'{str(os.environ[SPARKMASTER_PORT])}'
            )
                .newSession()
        )

        dataframe = spark_session.read.format(
            self.MONGO_SPARK_SOURCE).load()
        dataframe = dataframe.filter(
            dataframe[self.DOCUMENT_ID] != self.METADATA_FILE_ID
        )

        fields.append(self.DOCUMENT_ID)
        projection_dataframe = dataframe.select(*fields)
        projection_dataframe.write.format(self.MONGO_SPARK_SOURCE).mode(
            "append").save()

        spark_session.stop()

        self.metadata_creator.update_finished_flag(projection_filename, True)
