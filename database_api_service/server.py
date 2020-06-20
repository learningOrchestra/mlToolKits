from flask import jsonify, request, Flask
import os
from database import CsvDownloader, DatabaseApi, MongoOperations
from flask_cors import CORS

HTTP_STATUS_CODE_SUCESS = 200
HTTP_STATUS_CODE_SUCESS_CREATED = 201
HTTP_STATUS_CODE_NOT_ACCEPTABLE = 406
HTTP_STATUS_CODE_CONFLICT = 409

DATABASE_API_HOST = "DATABASE_API_HOST"
DATABASE_API_PORT = "DATABASE_API_PORT"

MESSAGE_RESULT = "result"

FILENAME = "filename"

FIRST_ARGUMENT = 0

MESSAGE_INVALID_URL = "invalid_url"
MESSAGE_DUPLICATE_FILE = "duplicate_file"
MESSAGE_CREATED_FILE = "file_created"
MESSAGE_DELETED_FILE = "deleted_file"

GET = 'GET'
POST = 'POST'
DELETE = 'DELETE'

app = Flask(__name__)
CORS(app)


@app.route('/files', methods=[POST])
def create_file():
    file_downloader_and_saver = CsvDownloader()
    mongo_operations = MongoOperations()
    database = DatabaseApi(mongo_operations, file_downloader_and_saver)

    try:
        database.add_file(
            request.json["url"],
            request.json[FILENAME])

    except Exception as error_message:

        if(error_message.args[FIRST_ARGUMENT] == MESSAGE_INVALID_URL):
            return jsonify(
                {MESSAGE_RESULT: error_message.args[FIRST_ARGUMENT]}),\
                    HTTP_STATUS_CODE_NOT_ACCEPTABLE

        elif(error_message.args[FIRST_ARGUMENT] == MESSAGE_DUPLICATE_FILE):
            return jsonify(
                {MESSAGE_RESULT: error_message.args[FIRST_ARGUMENT]}),\
                    HTTP_STATUS_CODE_CONFLICT

    return jsonify(
        {MESSAGE_RESULT: MESSAGE_CREATED_FILE}),\
        HTTP_STATUS_CODE_SUCESS_CREATED


@app.route('/files', methods=[GET])
def read_files():
    file_downloader_and_saver = CsvDownloader()
    mongo_operations = MongoOperations()
    database = DatabaseApi(mongo_operations, file_downloader_and_saver)

    if(request.args):
        file_result = database.read_file(
            request.args.get(FILENAME), request.args.get('skip'),
            request.args.get('limit'), request.args.get('query'))

        return jsonify(
            {MESSAGE_RESULT: file_result}), HTTP_STATUS_CODE_SUCESS

    else:
        return jsonify({MESSAGE_RESULT: database.get_files()}),\
            HTTP_STATUS_CODE_SUCESS


@app.route('/files', methods=[DELETE])
def delete_file():
    file_downloader_and_saver = CsvDownloader()
    mongo_operations = MongoOperations()
    database = DatabaseApi(mongo_operations, file_downloader_and_saver)

    result = database.delete_file(request.json[FILENAME])

    return jsonify(
        {MESSAGE_RESULT: MESSAGE_DELETED_FILE}),\
        HTTP_STATUS_CODE_SUCESS


if __name__ == "__main__":
    app.run(host=os.environ[DATABASE_API_HOST],
            port=int(os.environ[DATABASE_API_PORT]))
