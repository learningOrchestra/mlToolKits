from pyspark.sql import SparkSession, functions as sf
import os
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime
from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import StringIndexer, Tokenizer, VectorAssembler
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pymongo import MongoClient

SPARKMASTER_HOST = "SPARKMASTER_HOST"
SPARKMASTER_PORT = "SPARKMASTER_PORT"
SPARK_DRIVER_PORT = "SPARK_DRIVER_PORT"
MODEL_BUILDER_HOST_NAME = "MODEL_BUILDER_HOST_NAME"


class ModelBuilderInterface():
    def build_model(self, database_url_training, database_url_test, label):
        pass


class DatabaseInterface():
    def get_filenames(self):
        pass

    def find_one(self, filename, query):
        pass


class RequestValidatorInterface():
    MESSAGE_INVALID_TRAINING_FILENAME = "invalid_training_filename"
    MESSAGE_INVALID_TEST_FILENAME = "invalid_test_filename"
    MESSAGE_MISSING_LABEL = "missing_label"
    MESSAGE_INVALID_LABEL = "invalid_label"

    def training_filename_validator(self, training_filename):
        pass

    def test_filename_validator(self, test_filename):
        pass

    def field_validator(self, filename, file_field):
        pass


class SparkModelBuilder(ModelBuilderInterface):
    METADATA_DOCUMENT_ID = 0
    DOCUMENT_ID_NAME = "_id"

    def __init__(self):
        self.spark_session = SparkSession \
            .builder \
            .appName("model_builder") \
            .config("spark.driver.port",
                    os.environ[SPARK_DRIVER_PORT]) \
            .config("spark.driver.host",
                    os.environ[MODEL_BUILDER_HOST_NAME])\
            .config('spark.jars.packages',
                    'org.mongodb.spark:mongo-spark' +
                    '-connector_2.11:2.4.2')\
            .config("spark.memory.fraction", 0.8) \
            .config("spark.executor.memory", "1g") \
            .config("spark.sql.shuffle.partitions", "800") \
            .config("spark.memory.offHeap.enabled", 'true')\
            .config("spark.memory.offHeap.size", "1g")\
            .config("spark.scheduler.mode", "FAIR")\
            .master("spark://" +
                    os.environ[SPARKMASTER_HOST] +
                    ':' + str(os.environ[SPARKMASTER_PORT])) \
            .getOrCreate()

    def file_processor(self, database_url):
        file = self.spark_session.read.format("mongo").option(
            "uri", database_url).load()

        file_without_metadata = file.filter(
            file[self.DOCUMENT_ID_NAME] != self.METADATA_DOCUMENT_ID)

        metadata_fields = [
            "_id", "fields", "filename", "finished", "time_created",
            "url", "parent_filename"]
        processed_file = file_without_metadata.drop(*metadata_fields)

        return processed_file

    def fields_from_dataframe(self, dataframe, is_string):
        text_fields = []
        first_row = dataframe.first()

        if(is_string):
            for column in dataframe.schema.names:
                if(type(first_row[column]) == str):
                    text_fields.append(column)
        else:
            for column in dataframe.schema.names:
                if(type(first_row[column]) != str):
                    text_fields.append(column)

        return text_fields

    def build_model(self, database_url_training, database_url_test, label):
        training_df = self.file_processor(database_url_training)
        training_df = training_df.withColumnRenamed(label, "label")
        pre_processing_text = list()
        assembler_columns_input = []

        testing_df = self.file_processor(database_url_test)
        testing_df = testing_df.withColumn("label", sf.lit(0))

        string_fields = self.fields_from_dataframe(
            training_df, is_string=True)

        for column in string_fields:
            output_column_name = column + "_features"

            indexer = StringIndexer(
                            inputCol=column,
                            outputCol=output_column_name)

            training_indexer = indexer.fit(training_df)
            testing_indexer = indexer.fit(testing_df)

            training_df = training_indexer.transform(training_df)
            testing_df = testing_indexer.transform(testing_df)

            assembler_columns_input.append(output_column_name)

        training_number = self.fields_from_dataframe(
            training_df, is_string=False)

        for column in training_number:
            if(column != label):
                assembler_columns_input.append(column)

        assembler = VectorAssembler(
            inputCols=assembler_columns_input,
            outputCol="features")

        assembler.setHandleInvalid("skip")
        features_training = assembler.transform(training_df)
        features_testing = assembler.transform(testing_df)

        model = LogisticRegression(
            featuresCol="features", maxIter=10).fit(features_training)

        testing_prediction = model.transform(features_testing)

        for row in testing_prediction.collect():
            print(row, flush=True)

        self.spark_session.stop()


class MongoOperations(DatabaseInterface):

    def __init__(self, database_url, database_port, database_name):
        self.mongo_client = MongoClient(
            database_url, int(database_port))
        self.database = self.mongo_client[database_name]

    def get_filenames(self):
        return self.database.list_collection_names()

    def find_one(self, filename, query):
        file_collection = self.database[filename]
        return file_collection.find_one(query)


class ModelBuilderRequestValidator(RequestValidatorInterface):
    def __init__(self, database_connector):
        self.database = database_connector

    def training_filename_validator(self, training_filename):
        filenames = self.database.get_filenames()

        if(training_filename not in filenames):
            raise Exception(self.MESSAGE_INVALID_TRAINING_FILENAME)

    def test_filename_validator(self, test_filename):
        filenames = self.database.get_filenames()

        if(test_filename not in filenames):
            raise Exception(self.MESSAGE_INVALID_TEST_FILENAME)

    def field_validator(self, filename, file_field):
        if not file_field:
            raise Exception(self.MESSAGE_MISSING_LABEL)

        filename_metadata_query = {"filename": filename}

        filename_metadata = self.database.find_one(
            filename, filename_metadata_query)

        if file_field not in filename_metadata["fields"]:
            raise Exception(self.MESSAGE_INVALID_LABEL)
