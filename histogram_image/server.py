from flask import jsonify, Flask, request
import os
from histogram import (
    MongoOperations,
    HistogramRequestValidator,
    Histogram)

HTTP_STATUS_CODE_SUCESS = 200
HTTP_STATUS_CODE_SUCESS_CREATED = 201
HTTP_STATUS_CODE_NOT_ACCEPTABLE = 406
HTTP_STATUS_CODE_CONFLICT = 409

HISTOGRAM_HOST = "HISTOGRAM_HOST"
HISTOGRAM_PORT = "HISTOGRAM_PORT"

MESSAGE_RESULT = "result"

FIELDS_NAME = "fields"
HISTOGRAM_FILENAME_NAME = "histogram_filename"

FIRST_ARGUMENT = 0

MESSAGE_INVALID_URL = "invalid_url"
MESSAGE_DUPLICATE_FILE = "duplicate_file"
MESSAGE_CHANGED_FILE = "file_changed"
MESSAGE_DELETED_FILE = "deleted_file"

DATABASE_URL = "DATABASE_URL"
DATABASE_PORT = "DATABASE_PORT"
DATABASE_NAME = "DATABASE_NAME"
DATABASE_REPLICA_SET = "DATABASE_REPLICA_SET"

POST = "POST"

app = Flask(__name__)


def collection_database_url(database_url, database_name, database_filename,
                            database_replica_set):
    return database_url + '/' + \
        database_name + '.' + \
        database_filename + "?replicaSet=" + \
        database_replica_set + \
        "&authSource=admin"


@app.route('/histograms/<parent_filename>', methods=[POST])
def create_histogram(parent_filename):
    database = MongoOperations(
        os.environ[DATABASE_URL] + '/?replicaSet=' +
        os.environ[DATABASE_REPLICA_SET], os.environ[DATABASE_PORT],
        os.environ[DATABASE_NAME])

    request_validator = HistogramRequestValidator(database)

    try:
        request_validator.histogram_filename_validator(
            request.json[HISTOGRAM_FILENAME_NAME])
    except Exception as invalid_histogram_filename:
        return jsonify(
            {MESSAGE_RESULT:
                invalid_histogram_filename.args[FIRST_ARGUMENT]}),\
            HTTP_STATUS_CODE_CONFLICT

    try:
        request_validator.filename_validator(parent_filename)
    except Exception as invalid_filename:
        return jsonify(
            {MESSAGE_RESULT:
                invalid_filename.args[FIRST_ARGUMENT]}),\
            HTTP_STATUS_CODE_NOT_ACCEPTABLE

    try:
        request_validator.fields_validator(
            parent_filename, request.json[FIELDS_NAME])
    except Exception as invalid_fields:
        return jsonify(
            {MESSAGE_RESULT: invalid_fields.args[FIRST_ARGUMENT]}),\
            HTTP_STATUS_CODE_NOT_ACCEPTABLE

    histogram = Histogram(database)
    histogram.create_histogram(
        parent_filename,
        request.json[HISTOGRAM_FILENAME_NAME],
        request.json[FIELDS_NAME])

    return jsonify({MESSAGE_RESULT: MESSAGE_CHANGED_FILE}), \
        HTTP_STATUS_CODE_SUCESS


if __name__ == "__main__":
    app.run(host=os.environ[HISTOGRAM_HOST],
            port=int(os.environ[HISTOGRAM_PORT]))
