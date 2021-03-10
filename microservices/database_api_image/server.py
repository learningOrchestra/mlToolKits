from flask import jsonify, request, Flask
import os
from database import Dataset, Csv, Generic
from utils import Database, UserRequest, Metadata
from constants import Constants
import json

app = Flask(__name__)

database_connector = Database(
    os.environ[Constants.DATABASE_URL],
    os.environ[Constants.DATABASE_REPLICA_SET],
    int(os.environ[Constants.DATABASE_PORT]),
    os.environ[Constants.DATABASE_NAME])
request_validator = UserRequest(database_connector)
metadata_creator = Metadata(database_connector)


@app.route(Constants.MICROSERVICE_URI_PATH, methods=["POST"])
def create_file():
    service_type = request.args.get(Constants.TYPE_FIELD_NAME)
    url = request.json[Constants.URL_FIELD_NAME]
    filename = request.json[Constants.FILENAME_FIELD_NAME]

    request_errors = analyse_request_errors(
        request_validator,
        filename,
        url)

    if request_errors is not None:
        return request_errors

    if service_type == Constants.DATASET_CSV_TYPE:
        file_downloader = Csv(database_connector, metadata_creator)
    else:
        file_downloader = Generic(database_connector, metadata_creator)

    database = Dataset(file_downloader)

    database.add_file(url, filename)

    return (
        jsonify({
            Constants.MESSAGE_RESULT:
                f'{Constants.MICROSERVICE_URI_GET}'
                f'{request.json[Constants.FILENAME_FIELD_NAME]}'
                f'{Constants.MICROSERVICE_URI_GET_PARAMS}'}),
        Constants.HTTP_STATUS_CODE_SUCCESS_CREATED,
    )


@app.route(f'{Constants.MICROSERVICE_URI_PATH}/<filename>', methods=["GET"])
def read_files(filename):
    file_downloader = Csv(database_connector, metadata_creator)
    database = Dataset(file_downloader)

    limit = Constants.LIMIT_DEFAULT_VALUE
    skip = Constants.SKIP_DEFAULT_VALUE
    query = Constants.QUERY_DEFAULT_VALUE

    request_params = request.args.to_dict()
    if Constants.LIMIT_PARAM_NAME in request_params:
        limit = int(request_params[Constants.LIMIT_PARAM_NAME])
        if limit > Constants.LIMIT_PARAM_MAX:
            limit = Constants.LIMIT_PARAM_MAX

    if Constants.SKIP_PARAM_NAME in request_params:
        skip = int(request_params[Constants.SKIP_PARAM_NAME])
        if skip < Constants.SKIP_PARAM_MIN:
            skip = Constants.SKIP_PARAM_MIN

    if Constants.QUERY_PARAM_NAME in request_params:
        query = json.loads(request_params[Constants.QUERY_PARAM_NAME])

    file_result = database.read_file(
        filename, skip, limit, query
    )

    return jsonify({Constants.MESSAGE_RESULT: file_result}), \
           Constants.HTTP_STATUS_CODE_SUCCESS


@app.route(Constants.MICROSERVICE_URI_PATH, methods=["GET"])
def read_files_descriptor():
    service_type = request.args.get(Constants.TYPE_FIELD_NAME)

    file_downloader = Csv(database_connector, metadata_creator)
    database = Dataset(file_downloader)

    return jsonify(
        {Constants.MESSAGE_RESULT: database.get_metadata_files(
            service_type)}), \
           Constants.HTTP_STATUS_CODE_SUCCESS


@app.route(f'{Constants.MICROSERVICE_URI_PATH}/<filename>', methods=["DELETE"])
def delete_file(filename):
    service_type = request.args.get(Constants.TYPE_FIELD_NAME)

    if service_type == Constants.DATASET_CSV_TYPE:
        file_downloader = Csv(database_connector, metadata_creator)
    else:
        file_downloader = Generic(database_connector, metadata_creator)

    database = Dataset(file_downloader)
    database.delete_file(filename)

    return jsonify(
        {Constants.MESSAGE_RESULT:
             Constants.MESSAGE_DELETED_FILE}), \
           Constants.HTTP_STATUS_CODE_SUCCESS


def analyse_request_errors(request_validator: UserRequest, filename: str,
                           url: str):
    try:
        request_validator.filename_validator(
            filename
        )
    except Exception as invalid_filename:
        return (
            jsonify({Constants.MESSAGE_RESULT:
                         str(invalid_filename)}),
            Constants.HTTP_STATUS_CODE_CONFLICT,
        )

    try:
        request_validator.url_validator(url)
    except Exception as invalid_url:
        return (
            jsonify({Constants.MESSAGE_RESULT:
                         str(invalid_url)}),
            Constants.HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    return None


if __name__ == "__main__":
    app.run(host=os.environ[Constants.DATABASE_API_HOST],
            port=int(os.environ[Constants.DATABASE_API_PORT]))
