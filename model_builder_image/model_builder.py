from pyspark.sql import SparkSession
import os
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime
from pyspark.ml.classification import *
from pyspark.ml.feature import VectorAssembler
import jsonpickle

SPARKMASTER_HOST = "SPARKMASTER_HOST"
SPARKMASTER_PORT = "SPARKMASTER_PORT"
SPARK_DRIVER_PORT = "SPARK_DRIVER_PORT"
MODEL_BUILDER_HOST_NAME = "MODEL_BUILDER_HOST_NAME"


class ModelBuilderInterface():
    def build_model(self, database_url_training, database_url_test,
                    encoded_assembler, model_classificator_list):
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

    def build_model(self, database_url_training, database_url_test,
                    encoded_assembler, model_classificator_list):
        training_df = self.file_processor(database_url_training)
        testing_df = self.file_processor(database_url_test)

        assembler = jsonpickle.decode(encoded_assembler)

        features_training = assembler.transform(training_df)
        features_testing = assembler.transform(testing_df)

        classificator_switcher = {
            "lr": LogisticRegression(),
            "dt": DecisionTreeClassifier(),
            "rf": RandomForestClassifier(),
            "gb": GBTClassifier(),
            "nb": NaiveBayes(),
            "svc": LinearSVC()
        }

        for classificator_name in model_classificator_list:
            classificator = classificator_switcher[classificator_name]

            classificator.featuresCol = "features"
            classificator.maxIter = 10
            classificator.fit(features_training)

            testing_prediction = classificator.transform(features_testing)

            for row in testing_prediction.collect():
                print(row, flush=True)

        self.spark_session.stop()
