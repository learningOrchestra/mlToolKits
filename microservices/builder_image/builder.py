from pyspark.sql import SparkSession
import os
import time
import numpy as np  # Don't remove, the pyparsk uses the lib.
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from concurrent.futures import ThreadPoolExecutor

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
BUILDER_HOST_NAME = "BUILDER_HOST_NAME"


class Model:
    METADATA_DOCUMENT_ID = 0
    DOCUMENT_ID_NAME = "_id"

    def __init__(self, database_connector, metadata_creator,
                 database_url_training,
                 database_url_test):
        self.database = database_connector
        self.database_url_training = database_url_training
        self.database_url_test = database_url_test
        self.metadata_creator = metadata_creator

        self.thread_pool = ThreadPoolExecutor()

    def build(self, modeling_code, classifiers_list):
        classifiers_metadata = {}

        for classifier_name in classifiers_list:
            classifiers_metadata[classifier_name] = \
                self.metadata_creator.create_file(classifier_name)

        self.thread_pool.submit(self.pipeline, modeling_code,
                                classifiers_metadata)

    def pipeline(self, modeling_code, classifiers_metadata):
        spark_session = (
            SparkSession
                .builder
                .appName("builder")
                .config("spark.driver.port", os.environ[SPARK_DRIVER_PORT])
                .config("spark.driver.host",
                        os.environ[BUILDER_HOST_NAME])
                .config("spark.jars.packages",
                        "org.mongodb.spark:mongo-spark-connector_2.11:2.4.2",
                        )
                .config("spark.scheduler.mode", "FAIR")
                .config("spark.scheduler.pool", "builder")
                .config("spark.scheduler.allocation.file",
                        "./fairscheduler.xml")
                .master(
                f'spark://{os.environ[SPARKMASTER_HOST]}:'
                f'{str(os.environ[SPARKMASTER_PORT])}'
            )
                .getOrCreate()
        )

        (features_training, features_testing, features_evaluation) = \
            self.modeling_code_processing(
                modeling_code,
                spark_session)

        classifier_switcher = {
            "LR": LogisticRegression(),
            "DT": DecisionTreeClassifier(),
            "RF": RandomForestClassifier(),
            "GB": GBTClassifier(),
            "NB": NaiveBayes(),
        }
        classifier_threads = []

        for name, metadata in classifiers_metadata.items():
            classifier = classifier_switcher[name]
            classifier_threads.append(
                self.thread_pool.submit(
                    Model.classifier_processing,
                    classifier,
                    features_training,
                    features_testing,
                    features_evaluation,
                    metadata,
                )
            )

        for classifier in classifier_threads:
            testing_prediction, metadata_document = classifier.result()
            self.save_classifier_result(
                testing_prediction,
                metadata_document
            )

        spark_session.stop()

    def modeling_code_processing(self, modeling_code, spark_session):
        training_df = self.file_processor(
            self.database_url_training,
            spark_session)
        testing_df = self.file_processor(
            self.database_url_test,
            spark_session)

        preprocessing_variables = locals()
        exec(modeling_code, globals(), preprocessing_variables)

        features_training = preprocessing_variables["features_training"]
        features_testing = preprocessing_variables["features_testing"]
        features_evaluation = preprocessing_variables["features_evaluation"]

        return features_training, features_testing, features_evaluation

    @staticmethod
    def classifier_processing(
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

        return testing_prediction, metadata_document

    def save_classifier_result(self, predicted_df, filename_metadata):
        self.database.update_one(
            filename_metadata["datasetName"],
            filename_metadata,
            {self.DOCUMENT_ID_NAME: self.METADATA_DOCUMENT_ID})

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

        self.metadata_creator.update_finished_flag(
            filename_metadata["datasetName"], True)

    def file_processor(self, database_url, spark_session):
        file = spark_session.read.format("mongo").option(
            "uri", database_url).load()

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

    @staticmethod
    def create_prediction_filename(parent_filename, classifier_name):
        return f'{parent_filename}{classifier_name}'
