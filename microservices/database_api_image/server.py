from flask import jsonify, request, Flask
import os
from database import Dataset
from utils import Database, Csv, UserRequest
from concurrent.futures import ThreadPoolExecutor

HTTP_STATUS_CODE_SUCCESS = 200
HTTP_STATUS_CODE_SUCCESS_CREATED = 201
HTTP_STATUS_CODE_NOT_ACCEPTABLE = 406
HTTP_STATUS_CODE_CONFLICT = 409

DATABASE_API_HOST = "DATABASE_API_HOST"
DATABASE_API_PORT = "DATABASE_API_PORT"

MESSAGE_RESULT = "result"

DATABASE_URL = "DATABASE_URL"
DATABASE_PORT = "DATABASE_PORT"
DATABASE_NAME = "DATABASE_NAME"
DATABASE_REPLICA_SET = "DATABASE_REPLICA_SET"

FILENAME = "datasetName"
URL_FIELD_NAME = "datasetURI"

FIRST_ARGUMENT = 0

MESSAGE_INVALID_URL = "invalid url"
MESSAGE_DUPLICATE_FILE = "duplicate file"
MESSAGE_DELETED_FILE = "deleted file"

PAGINATE_FILE_LIMIT = 100

MICROSERVICE_URI_GET = "/api/learningOrchestra/v1/dataset/"
MICROSERVICE_URI_GET_PARAMS = "?query={}&limit=10&skip=0"

app = Flask(__name__)


@app.route("/files", methods=["POST"])
def create_file():
    url = request.json[URL_FIELD_NAME]
    filename = request.json[FILENAME]

    database_connector = Database(
        os.environ[DATABASE_URL],
        os.environ[DATABASE_REPLICA_SET],
        os.environ[DATABASE_PORT],
        os.environ[DATABASE_NAME])

    request_validator = UserRequest(database_connector)

    request_errors = analyse_request_errors(
        request_validator,
        filename,
        url)

    if request_errors is not None:
        return request_errors

    file_downloader = Csv(database_connector)
    database = Dataset(database_connector, file_downloader)

    database.add_file(url, filename)

    return (
        jsonify({
            MESSAGE_RESULT:
                MICROSERVICE_URI_GET +
                request.json[FILENAME] +
                MICROSERVICE_URI_GET_PARAMS}),
        HTTP_STATUS_CODE_SUCCESS_CREATED,
    )


@app.route("/files/<filename>", methods=["GET"])
def read_files(filename):
    database_connector = Database(
        os.environ[DATABASE_URL],
        os.environ[DATABASE_REPLICA_SET],
        os.environ[DATABASE_PORT],
        os.environ[DATABASE_NAME])

    file_downloader = Csv(database_connector)
    database = Dataset(database_connector, file_downloader)

    limit, skip, query = 20, 0, {}

    request_params = request.args.to_dict()
    if "limit" in request_params:
        if int(request_params["limit"]) < PAGINATE_FILE_LIMIT:
            limit = int(request_params["limit"])
    if "skip" in request_params:
        if int(request_params["skip"]) >= 0:
            skip = int(request_params["skip"])
    if "query" in request_params:
        query = request_params["query"]

    print(query, flush=True)
    print(type(query), flush=True)

    file_result = database.read_file(
        filename, skip, limit, query
    )

    return jsonify({MESSAGE_RESULT: file_result}), HTTP_STATUS_CODE_SUCCESS


@app.route("/files", methods=["GET"])
def read_files_descriptor():
    database_connector = Database(
        os.environ[DATABASE_URL],
        os.environ[DATABASE_REPLICA_SET],
        os.environ[DATABASE_PORT],
        os.environ[DATABASE_NAME])

    file_downloader = Csv(database_connector)
    database = Dataset(database_connector, file_downloader)

    return jsonify(
        {MESSAGE_RESULT: database.get_files(
            request.args.get("type"))}), HTTP_STATUS_CODE_SUCCESS


@app.route("/files/<filename>", methods=["DELETE"])
def delete_file(filename):
    database_connector = Database(
        os.environ[DATABASE_URL],
        os.environ[DATABASE_REPLICA_SET],
        os.environ[DATABASE_PORT],
        os.environ[DATABASE_NAME])

    file_downloader = Csv(database_connector)
    database = Dataset(database_connector, file_downloader)

    thread_pool = ThreadPoolExecutor()
    thread_pool.submit(database.delete_file, filename)

    return jsonify(
        {MESSAGE_RESULT: MESSAGE_DELETED_FILE}), HTTP_STATUS_CODE_SUCCESS


def analyse_request_errors(request_validator, filename, url):
    try:
        request_validator.filename_validator(
            filename
        )
    except Exception as invalid_filename:
        return (
            jsonify({MESSAGE_RESULT: invalid_filename.args[FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_CONFLICT,
        )

    try:
        request_validator.csv_url_validator(url)
    except Exception as invalid_url:
        return (
            jsonify({MESSAGE_RESULT: invalid_url.args[FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    return None


if __name__ == "__main__":
    app.run(host=os.environ[DATABASE_API_HOST],
            port=int(os.environ[DATABASE_API_PORT]), debug=True)
