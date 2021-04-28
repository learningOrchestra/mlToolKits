import pyspark.sql.session
from concurrent.futures import ThreadPoolExecutor
from utils import Metadata


class Projection:
    __FINISHED = "finished"
    __DOCUMENT_ID = "_id"
    __MONGO_SPARK_SOURCE = "com.mongodb.spark.sql.DefaultSource"
    __METADATA_FILE_ID = 0
    __database_url_output = None
    __MAX_NUMBER_THREADS = 3

    def __init__(self, metadata_creator: Metadata,
                 spark_session: pyspark.sql.session.SparkSession):
        self.__metadata_creator = metadata_creator
        self.__thread_pool = ThreadPoolExecutor()
        self.__spark_session = spark_session

    def create(self, parent_filename: str, projection_filename: str,
               fields: list, database_url_input: str,
               database_url_output: str) -> None:
        self.__metadata_creator.create_file(
            projection_filename,
            parent_filename,
            fields)

        self.__thread_pool.submit(self.__execute_spark_job,
                                  projection_filename, fields,
                                  database_url_input, database_url_output)

    def __execute_spark_job(self, projection_filename: str, fields: list,
                            database_url_input: str,
                            database_url_output: str) -> None:
        dataframe = self.__spark_session.read.format(
            self.__MONGO_SPARK_SOURCE).option(
            "spark.mongodb.input.uri", database_url_input).load()
        dataframe = dataframe.filter(
            dataframe[self.__DOCUMENT_ID] != self.__METADATA_FILE_ID
        )

        fields.append(self.__DOCUMENT_ID)
        projection_dataframe = dataframe.select(*fields)
        projection_dataframe.write.format(
            self.__MONGO_SPARK_SOURCE).mode("append").option(
            "spark.mongodb.output.uri", database_url_output).save()

        self.__metadata_creator.update_finished_flag(projection_filename, True)
