from pyspark.sql import SparkSession
import os
import time
import numpy as np
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime
import pytz
from pyspark.ml.classification import (
    LogisticRegression,
    DecisionTreeClassifier,
    RandomForestClassifier,
    GBTClassifier,
    NaiveBayes,
)

SPARKMASTER_HOST = "SPARKMASTER_HOST"
SPARKMASTER_PORT = "SPARKMASTER_PORT"
SPARK_DRIVER_PORT = "SPARK_DRIVER_PORT"
MODEL_BUILDER_HOST_NAME = "MODEL_BUILDER_HOST_NAME"


class SparkModelBuilder:
    METADATA_DOCUMENT_ID = 0
    DOCUMENT_ID_NAME = "_id"

    def __init__(self, database_connector):
        self.database = database_connector

        self.spark_session = (
            SparkSession.builder.appName("model_builder")
                .config("spark.driver.port", os.environ[SPARK_DRIVER_PORT])
                .config("spark.driver.host",
                        os.environ[MODEL_BUILDER_HOST_NAME])
                .config(
                "spark.jars.packages",
                "org.mongodb.spark:mongo-spark" + "-connector_2.11:2.4.2",
            )
                .config("spark.memory.fraction", 0.8)
                .config("spark.executor.memory", "1g")
                .config("spark.sql.shuffle.partitions", "800")
                .config("spark.memory.offHeap.enabled", "true")
                .config("spark.memory.offHeap.size", "1g")
                .config("spark.scheduler.mode", "FAIR")
                .config("spark.scheduler.pool", "model_builder")
                .config("spark.scheduler.allocation.file",
                        "./fairscheduler.xml")
                .master(
                "spark://"
                + os.environ[SPARKMASTER_HOST]
                + ":"
                + str(os.environ[SPARKMASTER_PORT])
            )
                .getOrCreate()
        )

        self.thread_pool = ThreadPoolExecutor()

    def file_processor(self, database_url):
        file = (
            self.spark_session.read.format("mongo").option("uri",
                                                           database_url).load()
        )

        file_without_metadata = file.filter(
            file[self.DOCUMENT_ID_NAME] != self.METADATA_DOCUMENT_ID
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

    def build_model(
            self,
            database_url_training,
            database_url_test,
            preprocessor_code,
            classificators_list,
            train_filename,
            test_filename,
    ):
        training_df = self.file_processor(database_url_training)
        testing_df = self.file_processor(database_url_test)

        preprocessing_variables = locals()
        exec(preprocessor_code, globals(), preprocessing_variables)

        features_training = preprocessing_variables["features_training"]
        features_testing = preprocessing_variables["features_testing"]
        features_evaluation = preprocessing_variables["features_evaluation"]

        classificator_switcher = {
            "lr": LogisticRegression(),
            "dt": DecisionTreeClassifier(),
            "rf": RandomForestClassifier(),
            "gb": GBTClassifier(),
            "nb": NaiveBayes(),
        }

        classificator_threads = []

        timezone_london = pytz.timezone("Etc/Greenwich")
        london_time = datetime.now(timezone_london)
        now_time = london_time.strftime("%Y-%m-%dT%H:%M:%S-00:00")

        metadata_document = {
            "parent_filename": train_filename,
            "time_created": now_time,
            "_id": 0,
            "type": "builder",
            "finished": False
        }

        for classificator_name in classificators_list:
            classificator = classificator_switcher[classificator_name]

            metadata_classifier = metadata_document.copy()
            metadata_classifier["classifier"] = classificator_name
            metadata_classifier[
                "filename"] = test_filename + "_" + classificator_name

            self.database.insert_one_in_file(
                metadata_classifier["filename"],
                metadata_classifier)

            classificator_threads.append(
                self.thread_pool.submit(
                    self.classificator_handler,
                    classificator,
                    features_training,
                    features_testing,
                    features_evaluation,
                    metadata_classifier,
                )
            )
        wait(classificator_threads)
        self.spark_session.stop()

    def classificator_handler(
            self,
            classificator,
            features_training,
            features_testing,
            features_evaluation,
            metadata_document
    ):

        classificator.featuresCol = "features"

        start_fit_model_time = time.time()
        model = classificator.fit(features_training)
        end_fit_model_time = time.time()

        fit_time = end_fit_model_time - start_fit_model_time
        metadata_document["fit_time"] = fit_time

        if features_evaluation is not None:
            evaluation_prediction = model.transform(features_evaluation)

            evaluator_f1 = MulticlassClassificationEvaluator(
                labelCol="label", predictionCol="prediction", metricName="f1"
            )

            evaluator_accuracy = MulticlassClassificationEvaluator(
                labelCol="label", predictionCol="prediction",
                metricName="accuracy"
            )

            evaluation_prediction.select("label", "prediction").show()

            model_f1 = evaluator_f1.evaluate(evaluation_prediction)
            model_accuracy = evaluator_accuracy.evaluate(evaluation_prediction)

            metadata_document["F1"] = str(model_f1)
            metadata_document["accuracy"] = str(model_accuracy)

        testing_prediction = model.transform(features_testing)

        self.save_classificator_result(
            testing_prediction,
            metadata_document
        )

    def save_classificator_result(self, predicted_df, filename_metatada):
        document_id = 1
        for row in predicted_df.collect():
            row_dict = row.asDict()
            row_dict["_id"] = document_id
            row_dict["probability"] = row_dict["probability"].toArray().tolist()

            document_id += 1

            del row_dict["features"]
            del row_dict["rawPrediction"]

            self.database.insert_one_in_file(filename_metatada["filename"],
                                             row_dict)

        flag_true_query = {"finished": True}
        metadata_file_query = {"_id": 0}
        self.database.update_one(filename_metatada["filename"], flag_true_query,
                                 metadata_file_query)


class MongoOperations:
    def __init__(self, database_url, replica_set, database_port, database_name):
        self.mongo_client = MongoClient(
            database_url + '/?replicaSet=' + replica_set, int(database_port))
        self.database = self.mongo_client[database_name]

    def get_filenames(self):
        return self.database.list_collection_names()

    def find_one(self, filename, query):
        file_collection = self.database[filename]
        return file_collection.find_one(query)

    def update_one(self, filename, new_value, query):
        new_values_query = {"$set": new_value}
        file_collection = self.database[filename]
        file_collection.update_one(query, new_values_query)

    def insert_one_in_file(self, filename, json_object):
        file_collection = self.database[filename]
        file_collection.insert_one(json_object)

    def delete_file(self, filename):
        file_collection = self.database[filename]
        file_collection.drop()

    @staticmethod
    def collection_database_url(database_url, database_name,
                                database_filename,
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


class ModelBuilderRequestValidator:
    MESSAGE_INVALID_TRAINING_FILENAME = "invalid_training_filename"
    MESSAGE_INVALID_TEST_FILENAME = "invalid_test_filename"
    MESSAGE_INVALID_CLASSIFICATOR = "invalid_classifier_name"
    MESSSAGE_INVALID_PREDICTION_NAME = "prediction_filename_already_exists"

    def __init__(self, database_connector):
        self.database = database_connector

    def training_filename_validator(self, training_filename):
        filenames = self.database.get_filenames()

        if training_filename not in filenames:
            raise Exception(self.MESSAGE_INVALID_TRAINING_FILENAME)

    def test_filename_validator(self, test_filename):
        filenames = self.database.get_filenames()

        if test_filename not in filenames:
            raise Exception(self.MESSAGE_INVALID_TEST_FILENAME)

    def predictions_filename_validator(self, test_filename, classificator_list):
        filenames = self.database.get_filenames()

        for classificator_name in classificator_list:
            prediction_filename = test_filename + "_" + classificator_name
            if prediction_filename in filenames:
                raise Exception(self.MESSSAGE_INVALID_PREDICTION_NAME)

    def model_classificators_validator(self, classificators_list):
        classificator_names_list = ["lr", "dt", "rf", "gb", "nb"]
        for classificator_name in classificators_list:
            if classificator_name not in classificator_names_list:
                raise Exception(self.MESSAGE_INVALID_CLASSIFICATOR)
