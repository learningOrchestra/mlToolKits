from pyspark.sql import SparkSession
import os
import time
import numpy as np # Don't remove, the pyparsk uses the lib.
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
            SparkSession.builder.appName("modelBuilder")
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

    def build_model(
            self,
            database_url_training,
            database_url_test,
            preprocessor_code,
            classifiers_list,
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

        classifier_switcher = {
            "LR": LogisticRegression(),
            "DT": DecisionTreeClassifier(),
            "RF": RandomForestClassifier(),
            "GB": GBTClassifier(),
            "NB": NaiveBayes(),
        }

        classifier_threads = []

        timezone_london = pytz.timezone("Etc/Greenwich")
        london_time = datetime.now(timezone_london)
        now_time = london_time.strftime("%Y-%m-%dT%H:%M:%S-00:00")

        metadata_document = {
            "parentDatasetName": [train_filename, test_filename],
            "timeCreated": now_time,
            "_id": 0,
            "type": "builder",
            "finished": False
        }

        for classifier_name in classifiers_list:
            classifier = classifier_switcher[classifier_name]

            metadata_classifier = metadata_document.copy()
            metadata_classifier["classifier"] = classifier_name
            metadata_classifier["datasetName"] = self.create_prediction_filename(
                test_filename,
                classifier_name)

            self.database.insert_one_in_file(
                metadata_classifier["datasetName"],
                metadata_classifier)

            classifier_threads.append(
                self.thread_pool.submit(
                    self.classifier_handler,
                    classifier,
                    features_training,
                    features_testing,
                    features_evaluation,
                    metadata_classifier,
                )
            )
        wait(classifier_threads)
        self.spark_session.stop()

    def classifier_handler(
            self,
            classifier,
            features_training,
            features_testing,
            features_evaluation,
            metadata_document
    ):

        classifier.featuresCol = "features"

        start_fit_model_time = time.time()
        model = classifier.fit(features_training)
        end_fit_model_time = time.time()

        fit_time = end_fit_model_time - start_fit_model_time
        metadata_document["fitTime"] = fit_time

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

        self.save_classifier_result(
            testing_prediction,
            metadata_document
        )

    def save_classifier_result(self, predicted_df, filename_metadata):
        document_id = 1
        for row in predicted_df.collect():
            row_dict = row.asDict()
            row_dict["_id"] = document_id
            row_dict["probability"] = row_dict["probability"].toArray().tolist()

            document_id += 1

            del row_dict["features"]
            del row_dict["rawPrediction"]

            self.database.insert_one_in_file(filename_metadata["datasetName"],
                                             row_dict)

        flag_true_query = {"finished": True}
        metadata_file_query = {"_id": 0}
        self.database.update_one(filename_metadata["datasetName"], flag_true_query,
                                 metadata_file_query)

    @staticmethod
    def create_prediction_filename(parent_filename, classifier_name):
        return parent_filename + classifier_name


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
    MESSAGE_INVALID_FILENAME = "invalid input dataset name"
    MESSAGE_INVALID_CLASSIFIER = "invalid classifier name"
    MESSAGE_INVALID_PREDICTION_NAME = "prediction dataset name already exists"
    MESSAGE_UNFINISHED_PROCESSING = "unfinished processing in input dataset"

    def __init__(self, database_connector):
        self.database = database_connector

    def parent_filename_validator(self, filename):
        filenames = self.database.get_filenames()

        if filename not in filenames:
            raise Exception(self.MESSAGE_INVALID_FILENAME)

    def finished_processing_validator(self, filename):
        filename_metadata_query = {"datasetName": filename}

        filename_metadata = self.database.find_one(filename,
                                                   filename_metadata_query)

        if filename_metadata["finished"] == False:
            raise Exception(self.MESSAGE_UNFINISHED_PROCESSING)

    def predictions_filename_validator(self, test_filename, classifier_list):
        filenames = self.database.get_filenames()

        for classifier_name in classifier_list:
            prediction_filename = SparkModelBuilder.create_prediction_filename(
                test_filename, classifier_name)
            if prediction_filename in filenames:
                raise Exception(self.MESSAGE_INVALID_PREDICTION_NAME)

    def model_classifiers_validator(self, classifiers_list):
        classifier_names_list = ["LR", "DT", "RF", "GB", "NB"]
        for classifier_name in classifiers_list:
            if classifier_name not in classifier_names_list:
                raise Exception(self.MESSAGE_INVALID_CLASSIFIER)
