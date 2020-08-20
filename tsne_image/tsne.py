from pyspark.sql import SparkSession
import os
from pymongo import MongoClient
import numpy as np
from sklearn.manifold import TSNE
from sklearn.preprocessing import OneHotEncoder
import seaborn as sns

SPARKMASTER_HOST = "SPARKMASTER_HOST"
SPARKMASTER_PORT = "SPARKMASTER_PORT"
SPARK_DRIVER_PORT = "SPARK_DRIVER_PORT"
TSNE_HOST_NAME = "TSNE_HOST_NAME"


class DatabaseInterface():
    def find_one(self, filename, query):
        pass

    def get_filenames(self):
        pass


class TsneInterface():
    def create_image(self, filename, tsne_filename):
        pass


class RequestValidatorInterface():
    MESSAGE_INVALID_FILENAME = "invalid_filename"
    MESSAGE_DUPLICATE_FILE = "duplicate_file"

    def parent_filename_validator(self, filename):
        pass

    def tsne_filename_validator(self, tsne_filename):
        pass


class TsneGenerator(TsneInterface):
    MONGO_SPARK_SOURCE = "com.mongodb.spark.sql.DefaultSource"
    DOCUMENT_ID = "_id"
    METADATA_FILE_ID = 0

    def __init__(self, database_url_input):
        self.spark_session = SparkSession \
            .builder \
            .appName("tsne") \
            .config("spark.mongodb.input.uri",
                    database_url_input) \
            .config("spark.driver.port",
                    os.environ[SPARK_DRIVER_PORT]) \
            .config("spark.driver.host",
                    os.environ[TSNE_HOST_NAME])\
            .config('spark.jars.packages',
                    'org.mongodb.spark:mongo-spark' +
                    '-connector_2.11:2.4.2')\
            .master("spark://" +
                    os.environ[SPARKMASTER_HOST] +
                    ':' + str(os.environ[SPARKMASTER_PORT])) \
            .getOrCreate()

    def create_image(self, filename, tsne_filename):
        dataframe = self.spark_session.read.format(
                self.MONGO_SPARK_SOURCE).load()
        dataframe = dataframe.filter(
            dataframe[self.DOCUMENT_ID] != self.METADATA_FILE_ID)

        dataframe = dataframe.dropna()
        pandas_dataframe = dataframe.toPandas()
        data_array = OneHotEncoder().fit_transform(pandas_dataframe).toarray()

        treated_array = np.array(data_array)
        embedded_array = TSNE().fit_transform(treated_array)

        sns_plot = sns.pairplot(embedded_array, size=2.5)
        sns_plot.savefig("/images/" + tsne_filename + '.png')


class MongoOperations(DatabaseInterface):

    def __init__(self, database_url, database_port, database_name):
        self.mongo_client = MongoClient(
            database_url, int(database_port))
        self.database = self.mongo_client[database_name]

    def find_one(self, filename, query):
        file_collection = self.database[filename]
        return file_collection.find_one(query)

    def get_filenames(self):
        return self.database.list_collection_names()


class TsneRequestValidator(RequestValidatorInterface):
    def __init__(self, database_connector):
        self.database = database_connector

    def parent_filename_validator(self, filename):
        filenames = self.database.get_filenames()

        if(filename not in filenames):
            raise Exception(self.MESSAGE_INVALID_FILENAME)

    def tsne_filename_validator(self, tsne_filename):
        images = os.listdir('.')
        if (tsne_filename + ".png") in images:
            raise Exception(self.MESSAGE_DUPLICATE_FILE)

