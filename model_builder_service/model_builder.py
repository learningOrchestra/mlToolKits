from pyspark.sql import SparkSession
import os
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime
from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import HashingTF, Tokenizer
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder

SPARKMASTER_HOST = "SPARKMASTER_HOST"
SPARKMASTER_PORT = "SPARKMASTER_PORT"
SPARK_DRIVER_PORT = "SPARK_DRIVER_PORT"
MODEL_BUILDER_HOST_NAME = "MODEL_BUILDER_HOST_NAME"


class ModelBuilderInterface():
    def build_model(self):
        pass


class SparkModelBuilder(ModelBuilderInterface):
    def __init__(self):
        self.database_url_output = database_url_output

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
                            .master("spark://" +
                                    os.environ[SPARKMASTER_HOST] +
                                    ':' + str(os.environ[SPARKMASTER_PORT])) \
                            .getOrCreate()

    def build_model(self):
        training = self.spark_session.createDataFrame([
            (0, "a b c d e spark", 1.0),
            (1, "b d", 0.0),
            (2, "spark f g h", 1.0),
            (3, "hadoop mapreduce", 0.0),
            (4, "b spark who", 1.0),
            (5, "g d a y", 0.0),
            (6, "spark fly", 1.0),
            (7, "was mapreduce", 0.0),
            (8, "e spark program", 1.0),
            (9, "a e c l", 0.0),
            (10, "spark compile", 1.0),
            (11, "hadoop software", 0.0)
        ], ["id", "text", "label"])

        tokenizer = Tokenizer(inputCol="text", outputCol="words")
        hashingTF = HashingTF(inputCol=tokenizer.getOutputCol(),
                              outputCol="features")
        lr = LogisticRegression(maxIter=10)
        pipeline = Pipeline(stages=[tokenizer, hashingTF, lr])

        paramGrid = ParamGridBuilder() \
            .addGrid(hashingTF.numFeatures, [10, 100, 1000]) \
            .addGrid(lr.regParam, [0.1, 0.01]) \
            .build()

        crossval = CrossValidator(estimator=pipeline,
                                  estimatorParamMaps=paramGrid,
                                  evaluator=BinaryClassificationEvaluator(),
                                  numFolds=2)  # use 3+ folds in practice

        cvModel = crossval.fit(training)

        test = self.spark_session.createDataFrame([
            (4, "spark i j k"),
            (5, "l m n"),
            (6, "mapreduce spark"),
            (7, "apache hadoop")
        ], ["id", "text"])

        prediction = cvModel.transform(test)
        selected = prediction.select("id", "text", "probability", "prediction")
        for row in selected.collect():
            print(row, flush=True)
