from pyspark.sql import SparkSession
import os
from pymongo import MongoClient
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder
import seaborn as sns
import pandas

SPARKMASTER_HOST = "SPARKMASTER_HOST"
SPARKMASTER_PORT = "SPARKMASTER_PORT"
SPARK_DRIVER_PORT = "SPARK_DRIVER_PORT"
PCA_HOST_NAME = "PCA_HOST_NAME"
IMAGES_PATH = "IMAGES_PATH"
IMAGE_FORMAT = ".png"


class PcaGenerator:
    MONGO_SPARK_SOURCE = "com.mongodb.spark.sql.DefaultSource"
    DOCUMENT_ID = "_id"
    METADATA_FILE_ID = 0

    def __init__(self, database_url_input):
        self.spark_session = (
            SparkSession.builder.appName("pca")
                .config("spark.mongodb.input.uri", database_url_input)
                .config("spark.driver.port", os.environ[SPARK_DRIVER_PORT])
                .config("spark.driver.host", os.environ[PCA_HOST_NAME])
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

    def create_image(self, label_name, pca_filename):
        dataframe = self.file_processor()
        dataframe = dataframe.dropna()
        string_fields = self.fields_from_dataframe(dataframe, is_string=True)

        label_enconder = LabelEncoder()
        encoded_dataframe = dataframe.toPandas()

        for field in string_fields:
            encoded_dataframe[field] = label_enconder.fit_transform(
                encoded_dataframe[field]
            )

        treated_array = np.array(encoded_dataframe)
        embedded_array = PCA(n_components=2).fit_transform(treated_array)
        embedded_array = pandas.DataFrame(embedded_array)
        image_path = os.environ[IMAGES_PATH] + "/" + pca_filename + IMAGE_FORMAT

        if label_name is not None:
            embedded_array[label_name] = encoded_dataframe[label_name]
            sns_plot = sns.scatterplot(x=0, y=1, data=embedded_array,
                                       hue=label_name)
            sns_plot.get_figure().savefig(image_path)
        else:
            sns_plot = sns.scatterplot(x=0, y=1, data=embedded_array)
            sns_plot.get_figure().savefig(image_path)

        self.spark_session.stop()

    def file_processor(self):
        file = self.spark_session.read.format(self.MONGO_SPARK_SOURCE).load()

        file_without_metadata = file.filter(
            file[self.DOCUMENT_ID] != self.METADATA_FILE_ID
        )

        metadata_fields = [
            "_id",
            "fields",
            "filename",
            "finished",
            "time_created",
            "url",
            "parent_filename",
            "type"
        ]
        processed_file = file_without_metadata.drop(*metadata_fields)

        return processed_file

    @staticmethod
    def fields_from_dataframe(dataframe, is_string):
        text_fields = []
        first_row = dataframe.first()

        if is_string:
            for column in dataframe.schema.names:
                if type(first_row[column]) == str:
                    text_fields.append(column)
        else:
            for column in dataframe.schema.names:
                if type(first_row[column]) != str:
                    text_fields.append(column)

        return text_fields


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
    def collection_database_url(database_url, database_name, database_filename,
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


class PcaRequestValidator:
    MESSAGE_INVALID_FILENAME = "invalid_filename"
    MESSAGE_DUPLICATE_FILE = "duplicate_file"
    MESSAGE_INVALID_LABEL = "invalid_field"
    MESSAGE_NOT_FOUND = "file_not_found"

    def __init__(self, database_connector):
        self.database = database_connector

    def parent_filename_validator(self, filename):
        filenames = self.database.get_filenames()

        if filename not in filenames:
            raise Exception(self.MESSAGE_INVALID_FILENAME)

    @staticmethod
    def pca_filename_existence_validator(pca_filename):
        images = os.listdir(os.environ[IMAGES_PATH])
        image_name = pca_filename + IMAGE_FORMAT
        if image_name in images:
            raise Exception(PcaRequestValidator.MESSAGE_DUPLICATE_FILE)

    @staticmethod
    def pca_filename_inexistence_validator(pca_filename):
        images = os.listdir(os.environ[IMAGES_PATH])
        image_name = pca_filename + IMAGE_FORMAT

        if image_name not in images:
            raise Exception(PcaRequestValidator.MESSAGE_NOT_FOUND)

    def filename_label_validator(self, filename, label):
        if label is None:
            return

        filename_metadata_query = {"filename": filename}

        filename_metadata = self.database.find_one(filename,
                                                   filename_metadata_query)

        if label not in filename_metadata["fields"]:
            raise Exception(self.MESSAGE_INVALID_LABEL)
