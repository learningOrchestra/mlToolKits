from pyspark.sql import SparkSession
import os
from datetime import datetime
import pytz
from pymongo import MongoClient

SPARKMASTER_HOST = "SPARKMASTER_HOST"
SPARKMASTER_PORT = "SPARKMASTER_PORT"
SPARK_DRIVER_PORT = "SPARK_DRIVER_PORT"
PROJECTION_HOST_NAME = "PROJECTION_HOST_NAME"


class SparkManager:
    FINISHED = "finished"
    DOCUMENT_ID = "_id"
    MONGO_SPARK_SOURCE = "com.mongodb.spark.sql.DefaultSource"
    METADATA_FILE_ID = 0
    database_url_output = None
    MAX_NUMBER_THREADS = 3

    def __init__(self, database_url_input, database_url_output):
        self.database_url_output = database_url_output

        self.spark_session = (
            SparkSession.builder.appName("projection")
                .config("spark.mongodb.input.uri", database_url_input)
                .config("spark.mongodb.output.uri", database_url_output)
                .config("spark.driver.port", os.environ[SPARK_DRIVER_PORT])
                .config("spark.driver.host", os.environ[PROJECTION_HOST_NAME])
                .config(
                "spark.jars.packages",
                "org.mongodb.spark:mongo-spark" + "-connector_2.11:2.4.2",
            )
                .master(
                "spark://"
                + os.environ[SPARKMASTER_HOST]
                + ":"
                + str(os.environ[SPARKMASTER_PORT])
            )
                .getOrCreate()
        )

    def projection(self, filename, projection_filename, fields):
        timezone_london = pytz.timezone("Etc/Greenwich")
        london_time = datetime.now(timezone_london)

        fields.append(self.DOCUMENT_ID)
        fields_without_id = fields.copy()

        try:
            fields_without_id.remove(self.DOCUMENT_ID)
        except Exception:
            pass

        metadata_content = (
            projection_filename,
            False,
            london_time.strftime("%Y-%m-%dT%H:%M:%S-00:00"),
            filename,
            self.METADATA_FILE_ID,
            fields_without_id,
            "projection"
        )

        metadata_fields = [
            "datasetName",
            self.FINISHED,
            "timeCreated",
            "parentDatasetName",
            self.DOCUMENT_ID,
            "fields",
            "type",
        ]

        metadata_dataframe = self.spark_session.createDataFrame(
            [metadata_content], metadata_fields
        )

        metadata_dataframe.write.format(self.MONGO_SPARK_SOURCE).save()

        self.submit_projection_job_spark(fields,
                                         metadata_content,
                                         metadata_fields)

    def submit_projection_job_spark(self, fields, metadata_content,
                                    metadata_fields):
        dataframe = self.spark_session.read.format(
            self.MONGO_SPARK_SOURCE).load()
        dataframe = dataframe.filter(
            dataframe[self.DOCUMENT_ID] != self.METADATA_FILE_ID
        )

        projection_dataframe = dataframe.select(*fields)
        projection_dataframe.write.format(self.MONGO_SPARK_SOURCE).mode(
            "append").save()

        metadata_content_list = list(metadata_content)
        metadata_content_list[metadata_content_list.index(False)] = True
        new_metadata_content = tuple(metadata_content_list)

        new_metadata_dataframe = self.spark_session.createDataFrame(
            [new_metadata_content], metadata_fields
        )

        new_metadata_dataframe.write.format(self.MONGO_SPARK_SOURCE).mode(
            "append"
        ).save()

        self.spark_session.stop()


class MongoOperations:
    def __init__(self, database_url, replica_set, database_port, database_name):
        self.mongo_client = MongoClient(
            database_url + '/?replicaSet=' + replica_set, int(database_port))
        self.database = self.mongo_client[database_name]

    def find_one(self, filename, query):
        file_collection = self.database[filename]
        return file_collection.find_one(query)

    def get_filenames(self):
        return self.database.list_collection_names()

    @staticmethod
    def collection_database_url(
            database_url, database_name, database_filename,
            database_replica_set
    ):
        return (
                database_url
                + "/"
                + database_name
                + "."
                + database_filename
                + "?replicaSet="
                + database_replica_set
                + "&authSource=admin"
        )


class ProjectionRequestValidator:
    MESSAGE_INVALID_FIELDS = "invalid fields"
    MESSAGE_INVALID_FILENAME = "invalid dataset name"
    MESSAGE_DUPLICATE_FILE = "duplicate file"
    MESSAGE_MISSING_FIELDS = "missing fields"
    MESSAGE_UNFINISHED_PROCESSING = "unfinished processing in input dataset"

    def __init__(self, database_connector):
        self.database = database_connector

    def filename_validator(self, filename):
        filenames = self.database.get_filenames()

        if filename not in filenames:
            raise Exception(self.MESSAGE_INVALID_FILENAME)

    def finished_processing_validator(self, filename):
        filename_metadata_query = {"datasetName": filename}

        filename_metadata = self.database.find_one(filename,
                                                   filename_metadata_query)

        if filename_metadata["finished"] == False:
            raise Exception(self.MESSAGE_UNFINISHED_PROCESSING)

    def projection_filename_validator(self, projection_filename):
        filenames = self.database.get_filenames()

        if projection_filename in filenames:
            raise Exception(self.MESSAGE_DUPLICATE_FILE)

    def projection_fields_validator(self, filename, projection_fields):
        if not projection_fields:
            raise Exception(self.MESSAGE_MISSING_FIELDS)

        filename_metadata_query = {"datasetName": filename}

        filename_metadata = self.database.find_one(filename,
                                                   filename_metadata_query)

        for field in projection_fields:
            if field not in filename_metadata["fields"]:
                raise Exception(self.MESSAGE_INVALID_FIELDS)
