from flask import jsonify, request, Flask
import os
from model_builder import (
    SparkModelBuilder,
    MongoOperations,
    ModelBuilderRequestValidator,
)
from concurrent.futures import ThreadPoolExecutor

HTTP_STATUS_CODE_SUCCESS_CREATED = 201
HTTP_STATUS_CODE_NOT_ACCEPTABLE = 406
HTTP_STATUS_CODE_CONFLICT = 409

MODEL_BUILDER_HOST_IP = "MODEL_BUILDER_HOST_IP"
MODEL_BUILDER_HOST_PORT = "MODEL_BUILDER_HOST_PORT"

MESSAGE_RESULT = "result"

DATABASE_URL = "DATABASE_URL"
DATABASE_PORT = "DATABASE_PORT"
DATABASE_NAME = "DATABASE_NAME"
DATABASE_REPLICA_SET = "DATABASE_REPLICA_SET"

TRAINING_FILENAME = "trainDatasetName"
TEST_FILENAME = "testDatasetName"
MODELING_CODE_NAME = "modelingCode"
CLASSIFIERS_NAME = "classifiersList"
FIRST_ARGUMENT = 0

MICROSERVICE_URI_GET = "/api/learningOrchestra/v1/builder/"
MICROSERVICE_URI_GET_PARAMS = "?query={}&limit=10&skip=0"

app = Flask(__name__)

thread_pool = ThreadPoolExecutor()


@app.route("/models", methods=["POST"])
def create_model():
    database = MongoOperations(
        os.environ[DATABASE_URL],
        os.environ[DATABASE_REPLICA_SET],
        os.environ[DATABASE_PORT],
        os.environ[DATABASE_NAME],
    )

    request_validator = ModelBuilderRequestValidator(database)

    request_errors = analyse_request_errors(
        request_validator,
        request.json[TRAINING_FILENAME],
        request.json[TEST_FILENAME],
        request.json[CLASSIFIERS_NAME])

    if request_errors is not None:
        return request_errors

    database_url_training = MongoOperations.collection_database_url(
        os.environ[DATABASE_URL],
        os.environ[DATABASE_NAME],
        request.json[TRAINING_FILENAME],
        os.environ[DATABASE_REPLICA_SET],
    )

    database_url_test = MongoOperations.collection_database_url(
        os.environ[DATABASE_URL],
        os.environ[DATABASE_NAME],
        request.json[TEST_FILENAME],
        os.environ[DATABASE_REPLICA_SET],
    )

    thread_pool.submit(
        model_builder_async_processing,
        database,
        database_url_training,
        database_url_test,
        request.json[MODELING_CODE_NAME],
        request.json[CLASSIFIERS_NAME],
        request.json[TRAINING_FILENAME],
        request.json[TEST_FILENAME],
    )

    return (
        jsonify({
            MESSAGE_RESULT:
                create_prediction_files_uri(
                    request.json[CLASSIFIERS_NAME],
                    request.json[TEST_FILENAME])}),
        HTTP_STATUS_CODE_SUCCESS_CREATED,
    )


def create_prediction_files_uri(classifiers_list, test_filename):
    classifiers_uri = []
    for classifier in classifiers_list:
        classifiers_uri.append(
            MICROSERVICE_URI_GET +
            SparkModelBuilder.create_prediction_filename(test_filename,
                                                         classifier) +
            MICROSERVICE_URI_GET_PARAMS)

    return classifiers_uri


def model_builder_async_processing(database, database_url_training,
                                   database_url_test, modeling_code,
                                   classifiers_name, train_filename,
                                   test_filename):
    model_builder = SparkModelBuilder(database)

    model_builder.build_model(
        database_url_training,
        database_url_test,
        modeling_code,
        classifiers_name,
        train_filename,
        test_filename,
    )


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
        request_validator.predictions_filename_validator(
            test_filename, classifiers_name)
    except Exception as invalid_prediction_filename:
        return (
            jsonify(
                {MESSAGE_RESULT: invalid_prediction_filename.args[
                    FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_CONFLICT,
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
        host=os.environ[MODEL_BUILDER_HOST_IP],
        port=int(os.environ[MODEL_BUILDER_HOST_PORT])
    )
