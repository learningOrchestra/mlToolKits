from pyspark.sql import SparkSession
import os
import numpy as np
from sklearn.manifold import TSNE
from sklearn.preprocessing import LabelEncoder
import seaborn as sns
import pandas

SPARKMASTER_HOST = "SPARKMASTER_HOST"
SPARKMASTER_PORT = "SPARKMASTER_PORT"
SPARK_DRIVER_PORT = "SPARK_DRIVER_PORT"
TSNE_HOST_NAME = "TSNE_HOST_NAME"
IMAGES_PATH = "IMAGES_PATH"


class Tsne:
    MONGO_SPARK_SOURCE = "com.mongodb.spark.sql.DefaultSource"
    DOCUMENT_ID = "_id"
    METADATA_FILE_ID = 0
    IMAGE_FORMAT = ".png"

    def __init__(self, database_url_input):
        self.database_url_input = database_url_input

    def create_image(self, label_name, tsne_filename):
        spark_session = (
            SparkSession
                .builder
                .appName("tsne")
                .config("spark.mongodb.input.uri", self.database_url_input)
                .config("spark.driver.port", os.environ[SPARK_DRIVER_PORT])
                .config("spark.driver.host", os.environ[TSNE_HOST_NAME])
                .config("spark.jars.packages",
                        "org.mongodb.spark:mongo-spark-connector_2.11:2.4.2",
                        )
                .master("spark://"
                        + os.environ[SPARKMASTER_HOST]
                        + ":"
                        + str(os.environ[SPARKMASTER_PORT])
                        )
                .getOrCreate()
        )

        dataframe = self.file_processor(spark_session)
        dataframe = dataframe.dropna()
        string_fields = self.fields_from_dataframe(dataframe, is_string=True)

        label_encoder = LabelEncoder()
        encoded_dataframe = dataframe.toPandas()

        for field in string_fields:
            encoded_dataframe[field] = label_encoder.fit_transform(
                encoded_dataframe[field]
            )

        treated_array = np.array(encoded_dataframe)
        embedded_array = TSNE().fit_transform(treated_array)
        embedded_array = pandas.DataFrame(embedded_array)
        image_path = os.environ[
                         IMAGES_PATH] + "/" + tsne_filename + self.IMAGE_FORMAT

        if label_name is not None:
            embedded_array[label_name] = encoded_dataframe[label_name]
            sns_plot = sns.scatterplot(x=0, y=1, data=embedded_array,
                                       hue=label_name)
            sns_plot.get_figure().savefig(image_path)
        else:
            sns_plot = sns.scatterplot(
                x=0,
                y=1,
                data=embedded_array,
            )
            sns_plot.get_figure().savefig(image_path)

        spark_session.stop()

    def file_processor(self, spark_session):
        file = spark_session.read.format(self.MONGO_SPARK_SOURCE).load()

        file_without_metadata = file.filter(
            file[self.DOCUMENT_ID] != self.METADATA_FILE_ID
        )

        metadata_fields = [
            "_id",
            "fields",
            "datasetName",
            "finished",
            "timeCreated",
            "url",
            "parentDatasetName",
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
