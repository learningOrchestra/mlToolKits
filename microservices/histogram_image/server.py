from flask import jsonify, Flask, request
import os
from histogram import MongoOperations, HistogramRequestValidator, Histogram
from concurrent.futures import ThreadPoolExecutor

HTTP_STATUS_CODE_SUCCESS_CREATED = 201
HTTP_STATUS_CODE_NOT_ACCEPTABLE = 406
HTTP_STATUS_CODE_CONFLICT = 409

HISTOGRAM_HOST = "HISTOGRAM_HOST"
HISTOGRAM_PORT = "HISTOGRAM_PORT"

MESSAGE_RESULT = "result"

FIELDS_NAME = "names"
HISTOGRAM_FILENAME_NAME = "output_filename"
PARENT_FILENAME_NAME = "input_filename"

FIRST_ARGUMENT = 0

MESSAGE_CREATED_FILE = "created_file"

DATABASE_URL = "DATABASE_URL"
DATABASE_PORT = "DATABASE_PORT"
DATABASE_NAME = "DATABASE_NAME"
DATABASE_REPLICA_SET = "DATABASE_REPLICA_SET"

MICROSERVICE_URI_GET = "/api/learningOrchestra/v1/explore/histogram/"
MICROSERVICE_URI_GET_PARAMS = "?query={}&limit=10&skip=0"

app = Flask(__name__)

thread_pool = ThreadPoolExecutor()


@app.route("/histograms", methods=["POST"])
def create_histogram():
    database = MongoOperations(
        os.environ[DATABASE_URL],
        os.environ[DATABASE_REPLICA_SET],
        os.environ[DATABASE_PORT],
        os.environ[DATABASE_NAME],
    )

    request_validator = HistogramRequestValidator(database)

    request_errors = analyse_request_errors(
        request_validator,
        request.json[PARENT_FILENAME_NAME],
        request.json[HISTOGRAM_FILENAME_NAME],
        request.json[FIELDS_NAME])

    if request_errors is not None:
        return request_errors

    thread_pool.submit(histogram_async_processing,
                       database,
                       request.json[PARENT_FILENAME_NAME],
                       request.json[HISTOGRAM_FILENAME_NAME],
                       request.json[FIELDS_NAME])

    return (
        jsonify({
            MESSAGE_RESULT:
                MICROSERVICE_URI_GET +
                request.json[HISTOGRAM_FILENAME_NAME] +
                MICROSERVICE_URI_GET_PARAMS}),
        HTTP_STATUS_CODE_SUCCESS_CREATED,
    )


def histogram_async_processing(database, parent_filename, histogram_filename,
                               fields_name):
    histogram = Histogram(database)
    histogram.create_histogram(
        parent_filename,
        histogram_filename,
        fields_name,
    )


def analyse_request_errors(request_validator, parent_filename,
                           histogram_filename, fields_name):
    try:
        request_validator.histogram_filename_validator(
            histogram_filename
        )
    except Exception as invalid_histogram_filename:
        return (
            jsonify({MESSAGE_RESULT: invalid_histogram_filename.args[
                FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_CONFLICT,
        )

    try:
        request_validator.filename_validator(parent_filename)
    except Exception as invalid_filename:
        return (
            jsonify({MESSAGE_RESULT: invalid_filename.args[FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    try:
        request_validator.fields_validator(parent_filename,
                                           fields_name)
    except Exception as invalid_fields:
        return (
            jsonify({MESSAGE_RESULT: invalid_fields.args[FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    try:
        request_validator.finished_processing_validator(parent_filename)
    except Exception as unfinished_filename:
        return jsonify(
            {MESSAGE_RESULT: unfinished_filename.args[FIRST_ARGUMENT]}), \
               HTTP_STATUS_CODE_NOT_ACCEPTABLE

    return None


if __name__ == "__main__":
    app.run(host=os.environ[HISTOGRAM_HOST],
            port=int(os.environ[HISTOGRAM_PORT]))
