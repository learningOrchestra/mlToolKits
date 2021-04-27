from flask import jsonify, request, Flask
import os
from builder import Builder
from pyspark.sql import SparkSession
from utils import Database, UserRequest, Metadata

HTTP_STATUS_CODE_SUCCESS_CREATED = 201
HTTP_STATUS_CODE_NOT_ACCEPTABLE = 406
HTTP_STATUS_CODE_CONFLICT = 409

BUILDER_HOST_IP = "BUILDER_HOST_IP"
BUILDER_HOST_PORT = "BUILDER_HOST_PORT"

MESSAGE_RESULT = "result"

DATABASE_URL = "DATABASE_URL"
DATABASE_PORT = "DATABASE_PORT"
DATABASE_NAME = "DATABASE_NAME"
DATABASE_REPLICA_SET = "DATABASE_REPLICA_SET"

SPARKMASTER_HOST = "SPARKMASTER_HOST"
SPARKMASTER_PORT = "SPARKMASTER_PORT"
SPARK_DRIVER_PORT = "SPARK_DRIVER_PORT"
BUILDER_HOST_NAME = "BUILDER_HOST_NAME"

TRAINING_FILENAME = "trainDatasetName"
TEST_FILENAME = "testDatasetName"
MODELING_CODE_NAME = "modelingCode"
CLASSIFIERS_NAME = "classifiersList"
FIRST_ARGUMENT = 0

MICROSERVICE_URI_GET = "/api/learningOrchestra/v1/builder/sparkml/"
MICROSERVICE_URI_GET_PARAMS = "?query={}&limit=10&skip=0"

app = Flask(__name__)
database_url = os.environ[DATABASE_URL]
database_replica_set = os.environ[DATABASE_REPLICA_SET]
database_name = os.environ[DATABASE_NAME]

database = Database(
    database_url,
    database_replica_set,
    os.environ[DATABASE_PORT],
    database_name,
)
request_validator = UserRequest(database)

metadata_creator = Metadata(database)

spark_session = SparkSession.builder.appName("builder/sparkml"). \
    config("spark.driver.port", os.environ[SPARK_DRIVER_PORT]). \
    config("spark.driver.host",
           os.environ[BUILDER_HOST_NAME]). \
    config("spark.jars.packages",
           "org.mongodb.spark:mongo-spark-connector_2.11:2.4.2",
           ). \
    config("spark.cores.max", 3). \
    config("spark.executor.cores", 2). \
    config("spark.executor.memory", "512m"). \
    config("spark.scheduler.mode", "FAIR"). \
    config("spark.scheduler.pool", "builder/sparkml"). \
    config("spark.scheduler.allocation.file",
           "./fairscheduler.xml"). \
    master(
    f'spark://{os.environ[SPARKMASTER_HOST]}:'
    f'{str(os.environ[SPARKMASTER_PORT])}'
).getOrCreate()


@app.route("/models", methods=["POST"])
def create_model():
    train_filename = request.json[TRAINING_FILENAME]
    test_filename = request.json[TEST_FILENAME]
    classifiers_name = request.json[CLASSIFIERS_NAME]

    request_errors = analyse_request_errors(
        request_validator,
        train_filename,
        test_filename,
        classifiers_name)

    if request_errors is not None:
        return request_errors

    database_url_training = Database.collection_database_url(
        database_url,
        database_name,
        train_filename,
        database_replica_set,
    )

    database_url_test = Database.collection_database_url(
        database_url,
        database_name,
        test_filename,
        database_replica_set,
    )
    builder = Builder(database, metadata_creator, spark_session)

    builder.build(
        request.json[MODELING_CODE_NAME],
        classifiers_name, train_filename,
        test_filename, database_url_training,
        database_url_test
    )

    return (
        jsonify({
            MESSAGE_RESULT:
                create_prediction_files_uri(
                    classifiers_name,
                    test_filename)}),
        HTTP_STATUS_CODE_SUCCESS_CREATED,
    )


def create_prediction_files_uri(classifiers_list, test_filename):
    classifiers_uri = []
    for classifier in classifiers_list:
        classifiers_uri.append(
            MICROSERVICE_URI_GET +
            Database.create_prediction_filename(test_filename,
                                                classifier) +
            MICROSERVICE_URI_GET_PARAMS)

    return classifiers_uri


def analyse_request_errors(request_validator, train_filename,
                           test_filename, classifiers_name):
    try:
        request_validator.parent_filename_validator(
            train_filename)
        request_validator.parent_filename_validator(
            test_filename)

    except Exception as invalid_filename:
        return (
            jsonify({MESSAGE_RESULT: invalid_filename.args[
                FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    try:
        request_validator.model_classifiers_validator(
            classifiers_name
        )
    except Exception as invalid_classifier_name:
        return (
            jsonify(
                {MESSAGE_RESULT: invalid_classifier_name.args[FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    try:
        request_validator.finished_processing_validator(
            train_filename)
        request_validator.finished_processing_validator(
            test_filename)
    except Exception as unfinished_filename:
        return jsonify(
            {MESSAGE_RESULT: unfinished_filename.args[FIRST_ARGUMENT]}), \
               HTTP_STATUS_CODE_NOT_ACCEPTABLE

    return None


if __name__ == "__main__":
    app.run(
        host=os.environ[BUILDER_HOST_IP],
        port=int(os.environ[BUILDER_HOST_PORT])
    )
