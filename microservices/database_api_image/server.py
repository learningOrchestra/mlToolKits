from flask import jsonify, request, Flask
import os
from database import CsvDownloader, DatabaseApi, MongoOperations
from concurrent.futures import ThreadPoolExecutor

HTTP_STATUS_CODE_SUCESS = 200
HTTP_STATUS_CODE_SUCESS_CREATED = 201
HTTP_STATUS_CODE_NOT_ACCEPTABLE = 406
HTTP_STATUS_CODE_CONFLICT = 409

DATABASE_API_HOST = "DATABASE_API_HOST"
DATABASE_API_PORT = "DATABASE_API_PORT"

MESSAGE_RESULT = "result"

FILENAME = "filename"
URL_FIELD_NAME = "url"

FIRST_ARGUMENT = 0

MESSAGE_INVALID_URL = "invalid_url"
MESSAGE_DUPLICATE_FILE = "duplicate_file"
MESSAGE_DELETED_FILE = "deleted_file"

GET = "GET"
POST = "POST"
DELETE = "DELETE"

PAGINATE_FILE_LIMIT = 20

app = Flask(__name__)


@app.route("/files", methods=[POST])
def create_file():
    file_downloader_and_saver = CsvDownloader()
    mongo_operations = MongoOperations()
    database = DatabaseApi(mongo_operations, file_downloader_and_saver)

    try:
        database.add_file(request.json[URL_FIELD_NAME], request.json[FILENAME])

    except Exception as error_message:

        if error_message.args[FIRST_ARGUMENT] == MESSAGE_INVALID_URL:
            return (
                jsonify({MESSAGE_RESULT: error_message.args[FIRST_ARGUMENT]}),
                HTTP_STATUS_CODE_NOT_ACCEPTABLE,
            )

        elif error_message.args[FIRST_ARGUMENT] == MESSAGE_DUPLICATE_FILE:
            return (
                jsonify({MESSAGE_RESULT: error_message.args[FIRST_ARGUMENT]}),
                HTTP_STATUS_CODE_CONFLICT,
            )

    return (
        jsonify({MESSAGE_RESULT:
                     "/api/learningOrchestra/v1/dataset/" +
                     request.json[FILENAME] +
                     "?query={}&limit=10&skip=0"}),
        HTTP_STATUS_CODE_SUCESS_CREATED,
    )


@app.route("/files/<filename>", methods=[GET])
def read_files(filename):
    file_downloader_and_saver = CsvDownloader()
    mongo_operations = MongoOperations()
    database = DatabaseApi(mongo_operations, file_downloader_and_saver)

    limit = int(request.args.get("limit"))
    if limit > PAGINATE_FILE_LIMIT:
        limit = PAGINATE_FILE_LIMIT

    file_result = database.read_file(
        filename, request.args.get("skip"), limit, request.args.get("query")
    )

    return jsonify({MESSAGE_RESULT: file_result}), HTTP_STATUS_CODE_SUCESS


@app.route("/files", methods=[GET])
def read_files_descriptor():
    file_downloader_and_saver = CsvDownloader()
    mongo_operations = MongoOperations()
    database = DatabaseApi(mongo_operations, file_downloader_and_saver)

    return jsonify(
        {MESSAGE_RESULT: database.get_files()}), HTTP_STATUS_CODE_SUCESS


@app.route("/files/<filename>", methods=[DELETE])
def delete_file(filename):
    file_downloader_and_saver = CsvDownloader()
    mongo_operations = MongoOperations()
    database = DatabaseApi(mongo_operations, file_downloader_and_saver)

    thread_pool = ThreadPoolExecutor()
    thread_pool.submit(database.delete_file, filename)

    return jsonify(
        {MESSAGE_RESULT: MESSAGE_DELETED_FILE}), HTTP_STATUS_CODE_SUCESS


if __name__ == "__main__":
    app.run(host=os.environ[DATABASE_API_HOST],
            port=int(os.environ[DATABASE_API_PORT]))
