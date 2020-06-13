from pyspark.sql import SparkSession
import os
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime
import pytz
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StringType, StructField,
    StructType, BooleanType,
    IntegerType
)

SPARKMASTER_HOST = "SPARKMASTER_HOST"
SPARKMASTER_PORT = "SPARKMASTER_PORT"
SPARK_DRIVER_PORT = "SPARK_DRIVER_PORT"
PROJECTION_HOST_NAME = "PROJECTION_HOST_NAME"


class ProcessorInterface():
    MESSAGE_CREATED_FILE = "file_created"
    MESSAGE_DUPLICATE_FILE = "duplicate_file"
    MESSAGE_INVALID_FIELDS = "invalid_fields"

    def projection(self, filename, projection_filename, fields):
        pass


class SparkManager(ProcessorInterface):
    FINISHED = "finished"
    DOCUMENT_ID = '_id'
    MONGO_SPARK_SOURCE = "com.mongodb.spark.sql.DefaultSource"
    METADATA_FILE_ID = 0
    database_url_output = None

    def __init__(self, database_url_input, database_url_output):
        self.database_url_output = database_url_output

        self.spark_session = SparkSession \
                            .builder \
                            .appName("projection") \
                            .config("spark.mongodb.input.uri",
                                    database_url_input) \
                            .config("spark.mongodb.output.uri",
                                    database_url_output) \
                            .config("spark.driver.port",
                                    os.environ[SPARK_DRIVER_PORT]) \
                            .config("spark.driver.host",
                                    os.environ[PROJECTION_HOST_NAME])\
                            .config('spark.jars.packages',
                                    'org.mongodb.spark:mongo-spark' +
                                    '-connector_2.11:2.4.2')\
                            .master("spark://" +
                                    os.environ[SPARKMASTER_HOST] +
                                    ':' + str(os.environ[SPARKMASTER_PORT])) \
                            .getOrCreate()

        self.thread_pool = ThreadPoolExecutor()

    def projection(self, filename, projection_filename, fields):
        dataframe = self.spark_session.read.format(
                self.MONGO_SPARK_SOURCE).load()
        dataframe = dataframe.filter(
            dataframe[self.DOCUMENT_ID] == self.METADATA_FILE_ID)

        parent_file_fields = dataframe.select("fields").collect()

        fields_without_id = list(fields).remove(self.DOCUMENT_ID)

        for field in fields:
            if fields_without_id not in parent_file_fields:
                return self.MESSAGE_INVALID_FIELDS

        timezone_london = pytz.timezone('Etc/Greenwich')
        london_time = datetime.now(timezone_london)

        metadata_content = (projection_filename,
                            False,
                            london_time.strftime("%Y-%m-%dT%H:%M:%S-00:00"),
                            filename,
                            self.METADATA_FILE_ID,
                            fields_without_id)

        metadata_fields = ["filename",
                           self.FINISHED,
                           "time_created",
                           "parent_filename",
                           self.DOCUMENT_ID,
                           "fields"]

        metadata_dataframe = self.spark_session.createDataFrame(
                        [metadata_content],
                        metadata_fields)
        try:
            metadata_dataframe.write.format(
                    self.MONGO_SPARK_SOURCE).save()
        except Exception:
            return self.MESSAGE_DUPLICATE_FILE

        self.thread_pool.submit(
            self.submit_projection_job_spark,
            fields, metadata_content, metadata_fields)

        return self.MESSAGE_CREATED_FILE

    def submit_projection_job_spark(self, fields, metadata_content,
                                    metadata_fields):
        dataframe = self.spark_session.read.format(
                self.MONGO_SPARK_SOURCE).load()
        dataframe = dataframe.filter(
            dataframe[self.DOCUMENT_ID] != self.METADATA_FILE_ID)

        projection_dataframe = dataframe.select(*fields)
        projection_dataframe.write.format(
                self.MONGO_SPARK_SOURCE).mode("append").save()

        metadata_content_list = list(metadata_content)
        metadata_content_list[metadata_content_list.index(False)] = True
        new_metadata_content = tuple(metadata_content_list)

        new_metadata_dataframe = self.spark_session.createDataFrame(
                        [new_metadata_content],
                        metadata_fields)

        new_metadata_dataframe.write.format(
                self.MONGO_SPARK_SOURCE).mode("append").save()
