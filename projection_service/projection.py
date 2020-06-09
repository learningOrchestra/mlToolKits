from pyspark.sql import SparkSession
import os
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime
import pytz
from pyspark.sql import functions as F

SPARKMASTER_HOST = "SPARKMASTER_HOST"
SPARKMASTER_PORT = "SPARKMASTER_PORT"
SPARK_DRIVER_PORT = "SPARK_DRIVER_PORT"


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
                        ("filename",
                         self.FINISHED,
                         "time_created",
                         "parent_filename",
                         self.DOCUMENT_ID))

        metadata_dataframe.write.format(
                self.MONGO_SPARK_SOURCE).save()

        '''self.thread_pool.submit(
            self.submit_projection_job_spark,
            fields)'''

        self.submit_projection_job_spark(fields)

    def submit_projection_job_spark(self, fields):
        data_frame = self.spark_session.read.format(
                self.MONGO_SPARK_SOURCE).load()

        data_frame = data_frame.filter(
            data_frame[self.DOCUMENT_ID] != self.METADATA_FILE_ID)

        projection_data_frame = data_frame.select(*fields)

        projection_data_frame.write.format(
                self.MONGO_SPARK_SOURCE).save()

        resulted_data_frame = self.spark_session.read.format(
                self.MONGO_SPARK_SOURCE).load()

        metadata_data_frame = resulted_data_frame.filter(
                resulted_data_frame[self.DOCUMENT_ID] == self.METADATA_FILE_ID)

        metadata_data_frame.withColumn(
            self.FINISHED,
            F.when(F.col(self.FINISHED) == False, True))

        metadata_data_frame.write.format(
                self.MONGO_SPARK_SOURCE).save()
