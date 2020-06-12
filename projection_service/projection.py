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
    def projection(self, filename, projection_filename, fields):
        pass


class SparkManager(ProcessorInterface):
    MESSAGE_CREATED_FILE = "file_created"
    FINISHED = "finished"
    DOCUMENT_ID = '_id'
    MONGO_SPARK_SOURCE = "com.mongodb.spark.sql.DefaultSource"
    METADATA_FILE_ID = 0

    def __init__(self, database_url_input, database_url_output):
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
        timezone_london = pytz.timezone('Etc/Greenwich')
        london_time = datetime.now(timezone_london)

        metadata_dataframe = self.spark_session.createDataFrame(
                        [(projection_filename,
                         False,
                         london_time.strftime("%Y-%m-%dT%H:%M:%S-00:00"),
                         filename,
                         self.METADATA_FILE_ID)],
                        ["filename",
                         self.FINISHED,
                         "time_created",
                         "parent_filename",
                         self.DOCUMENT_ID])

        metadata_dataframe.write.format(
                self.MONGO_SPARK_SOURCE).save()

        '''self.thread_pool.submit(
            self.submit_projection_job_spark,
            fields)'''

        self.submit_projection_job_spark(fields, metadata_dataframe)

    def submit_projection_job_spark(self, fields, metadata_dataframe):
        dataframe = self.spark_session.read.format(
                self.MONGO_SPARK_SOURCE).load()
        dataframe = dataframe.filter(
            dataframe[self.DOCUMENT_ID] != self.METADATA_FILE_ID)

        projection_dataframe = dataframe.select(*fields)
        projection_dataframe.write.format(
                self.MONGO_SPARK_SOURCE).mode("append").save()

        '''metadata_schema = StructType([
                StructField("filename", StringType(), False),
                StructField(self.FINISHED, BooleanType(), False),
                StructField("time_created", StringType(), False),
                StructField("parent_filename", StringType(), False),
                StructField(self.DOCUMENT_ID, IntegerType(), False)
        ])

        resulted_dataframe = self.spark_session.read.schema(
                metadata_schema).format(
                    self.MONGO_SPARK_SOURCE).load()

         metadata_dataframe = resulted_dataframe.filter(
                resulted_data_frame[self.DOCUMENT_ID] == self.METADATA_FILE_ID)

        new_metadata_data_frame = resulted_dataframe.withColumn(
            self.FINISHED,
            F.when(F.col(self.FINISHED) == False, True))

        new_metadata_data_frame.write.format(
                self.MONGO_SPARK_SOURCE).mode("append").save()'''

        metadata_dataframe = metadata_dataframe.withColumn(
            self.FINISHED,
            F.when(F.col(self.FINISHED) == False, True)
            .otherwise(F.col(self.FINISHED)))

        metadata_dataframe.write.format(
                self.MONGO_SPARK_SOURCE).mode("overwrite").save()
