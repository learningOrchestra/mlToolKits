from flask import jsonify, request, Flask
import os
from .model_preprocessor import (
    SparkModelPreProcessor,
    MongoOperations,
    ModelPreprocessorRequestValidator)

HTTP_STATUS_CODE_SUCESS_CREATED = 201
HTTP_STATUS_CODE_NOT_ACCEPTABLE = 406

MODEL_PREPROCESSOR_HOST_IP = "MODEL_PREPROCESSOR_HOST_IP"
MODEL_PREPROCESSOR_HOST_PORT = "MODEL_PREPROCESSOR_HOST_PORT"

GET = 'GET'
POST = 'POST'
DELETE = 'DELETE'

MESSAGE_RESULT = "result"
MESSAGE_CREATED_FILE = "created_file"

DATABASE_URL = "DATABASE_URL"
DATABASE_PORT = "DATABASE_PORT"
DATABASE_NAME = "DATABASE_NAME"
DATABASE_REPLICA_SET = "DATABASE_REPLICA_SET"


TRAINING_FILENAME = "training_filename"
TEST_FILENAME = "test_filename"
PREPROCESSOR_CODE_NAME = "preprocessor_code"
MODEL_CLASSIFICATOR = "model_classificator"
FIRST_ARGUMENT = 0

app = Flask(__name__)


def collection_database_url(database_url, database_name, database_filename,
                            database_replica_set):
    return database_url + '/' + \
        database_name + '.' + \
        database_filename + "?replicaSet=" + \
        database_replica_set + \
        "&authSource=admin"


@app.route('/preprocessors', methods=[POST])
def create_preprocessor_model():
    database = MongoOperations(
        os.environ[DATABASE_URL] + '/?replicaSet=' +
        os.environ[DATABASE_REPLICA_SET], os.environ[DATABASE_PORT],
        os.environ[DATABASE_NAME])

    request_validator = ModelPreprocessorRequestValidator(database)

    try:
        request_validator.training_filename_validator(
            request.json[TRAINING_FILENAME])
    except Exception as invalid_training_filename:
        return jsonify(
            {MESSAGE_RESULT:
                invalid_training_filename.args[FIRST_ARGUMENT]}),\
            HTTP_STATUS_CODE_NOT_ACCEPTABLE

    try:
        request_validator.test_filename_validator(
            request.json[TEST_FILENAME])
    except Exception as invalid_test_filename:
        return jsonify(
            {MESSAGE_RESULT: invalid_test_filename.args[FIRST_ARGUMENT]}),\
            HTTP_STATUS_CODE_NOT_ACCEPTABLE

    try:
        request_validator.model_classificators_validator(
            request.json[MODEL_CLASSIFICATOR])
    except Exception as invalid_classificator_name:
        return jsonify(
            {MESSAGE_RESULT:
                invalid_classificator_name.args[FIRST_ARGUMENT]}),\
            HTTP_STATUS_CODE_NOT_ACCEPTABLE

    database_url_training = collection_database_url(
                            os.environ[DATABASE_URL],
                            os.environ[DATABASE_NAME],
                            request.json[TRAINING_FILENAME],
                            os.environ[DATABASE_REPLICA_SET])

    database_url_test = collection_database_url(
                            os.environ[DATABASE_URL],
                            os.environ[DATABASE_NAME],
                            request.json[TEST_FILENAME],
                            os.environ[DATABASE_REPLICA_SET])

    model_preprocessor = SparkModelPreProcessor()
    model_builder_sender = ModelBuilderDataSender()

    model_preprocessor.preprocessor(
        database_url_training, database_url_test,
        request.json[PREPROCESSOR_CODE_NAME],
        model_builder_sender
    )

    return jsonify({MESSAGE_RESULT: MESSAGE_CREATED_FILE}), \
        HTTP_STATUS_CODE_SUCESS_CREATED


if __name__ == "__main__":
    app.run(host=os.environ[MODEL_PREPROCESSOR_HOST_IP],
            port=int(os.environ[MODEL_PREPROCESSOR_HOST_PORT]), debug=True)
