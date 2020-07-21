from pyspark.sql import SparkSession
import os
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime
from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import HashingTF, Tokenizer, VectorAssembler
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
            .config("spark.memory.offHeap.enabled", 'true')\
            .config("spark.memory.offHeap.size", "2g")\
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
            "_id", "fields", "filename", "finished", "time_created", "url"]
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
        training_file = self.file_processor(database_url_training)
        training_file = training_file.withColumnRenamed(label, "label")

        pre_processing_text = list()
        assembler_columns_input = []

        training_string_fields = self.fields_from_dataframe(
            training_file, True)

        for column in training_string_fields:
            tokenizer = Tokenizer(
                inputCol=column, outputCol=(column + "_words"))
            pre_processing_text.append(tokenizer)

            hashing_tf_output_column_name = column + "_features"

            hashing_tf = HashingTF(
                            inputCol=tokenizer.getOutputCol(),
                            outputCol=hashing_tf_output_column_name)
            pre_processing_text.append(hashing_tf)
            assembler_columns_input.append(hashing_tf_output_column_name)

        training_number_fields = self.fields_from_dataframe(
            training_file, False)

        for column in training_number_fields:
            if(column != label):
                assembler_columns_input.append(column)

        assembler = VectorAssembler(
            inputCols=assembler_columns_input,
            outputCol="features")

        assembler.setHandleInvalid("skip")

        logistic_regression = LogisticRegression(maxIter=10)

        pipeline = Pipeline(
            stages=[*pre_processing_text, assembler, logistic_regression])
        param_grid = ParamGridBuilder().build()
        cross_validator = CrossValidator(
                            estimator=pipeline,
                            estimatorParamMaps=param_grid,
                            evaluator=BinaryClassificationEvaluator(),
                            numFolds=2)
        cross_validator_model = cross_validator.fit(training_file)

        test_file = self.file_processor(database_url_test)
        prediction = cross_validator_model.transform(test_file)

        for row in prediction.collect():
            print(row, flush=True)
        '''

        ##############################

        training_dataframe = self.file_processor(database_url_training)

        assembler_columns_input = []

        training_string_fields = self.fields_from_dataframe(
            training_dataframe, True)

        for column in training_string_fields:
            tokenizer_output_column_name = column + "_words"
            hashing_tf_output_column_name = column + "_features"

            tokenizer = Tokenizer(
                inputCol=column, outputCol=tokenizer_output_column_name)
            tokens = tokenizer.transform(training_dataframe)

            hashing_tf = HashingTF(
                inputCol=tokenizer.getOutputCol(),
                outputCol=hashing_tf_output_column_name)

            assembler_columns_input.append(hashing_tf.transform(tokens))

        training_number_fields = self.fields_from_dataframe(
            training_dataframe, False)

        for column in training_number_fields:
            if(column != label):
                assembler_columns_input.append(column)

        assembler = VectorAssembler(
            inputCols=assembler_columns_input,
            outputCol="features").setHandleInvalid("skip")

        pipeline = Pipeline(stages=[assembler, logistic_regression])
        pipeline_model = pipeline.fit(training_dataframe)

        training_dataframe_transformed =\
            pipelineModel.transform(training_dataframe)

        logistic_regression = LogisticRegression(maxIter=10, labelCol=label)

        param_grid = ParamGridBuilder().build()
        cross_validator = CrossValidator(
                            estimator=pipeline_model,
                            estimatorParamMaps=param_grid,
                            evaluator=BinaryClassificationEvaluator(),
                            numFolds=2)
        cross_validator_model = cross_validator.fit(
            training_dataframe_transformed)

        test_dataframe = self.file_processor(database_url_test)
        prediction = cross_validator_model.transform(test_dataframe)

        for row in prediction.collect():
            print(row, flush=True)
'''


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
