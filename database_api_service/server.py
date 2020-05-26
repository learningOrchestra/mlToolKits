from flask import jsonify, request, Flask
import os
from database import FileDownloaderAndSaver, DatabaseApi, MongoOperations
from flask_cors import CORS

HTTP_STATUS_CODE_SUCESS = 200
HTTP_STATUS_CODE_SUCESS_CREATED = 201
HTTP_STATUS_CODE_SERVER_ERROR = 500

DATABASE_API_HOST = "DATABASE_API_HOST"
DATABASE_API_PORT = "DATABASE_API_PORT"

MESSAGE_RESULT = "result"

FILENAME = "filename"

GET = 'GET'
POST = 'POST'
DELETE = 'DELETE'

app = Flask(__name__)
CORS(app)


@app.route('/files', methods=[POST])
def create_file():
    file_downloader_and_saver = FileDownloaderAndSaver()
    mongo_operations = MongoOperations()
    database = DatabaseApi(mongo_operations, file_downloader_and_saver)

    result = database.add_file(
        request.json["url"],
        request.json[FILENAME])

    if(result == DatabaseApi.MESSAGE_INVALID_URL):
        return jsonify(
            {MESSAGE_RESULT: DatabaseApi.MESSAGE_INVALID_URL}),\
                HTTP_STATUS_CODE_SERVER_ERROR

    elif(result == DatabaseApi.MESSAGE_DUPLICATE_FILE):
        return jsonify(
            {MESSAGE_RESULT: DatabaseApi.MESSAGE_DUPLICATE_FILE}),\
                HTTP_STATUS_CODE_SERVER_ERROR

    else:
        return jsonify(
            {MESSAGE_RESULT: DatabaseApi.MESSAGE_CREATED_FILE}),\
                HTTP_STATUS_CODE_SUCESS_CREATED


@app.route('/files', methods=[GET])
def read_files():
    file_downloader_and_saver = FileDownloaderAndSaver()
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
    file_downloader_and_saver = FileDownloaderAndSaver()
    mongo_operations = MongoOperations()
    database = DatabaseApi(mongo_operations, file_downloader_and_saver)

    result = database.delete_file(request.json[FILENAME])

    if(result == DatabaseApi.MESSAGE_DELETED_FILE):
        return jsonify(
            {MESSAGE_RESULT: DatabaseApi.MESSAGE_DELETED_FILE}),\
                HTTP_STATUS_CODE_SUCESS


if __name__ == "__main__":
    app.run(host=os.environ[DATABASE_API_HOST],
            port=int(os.environ[DATABASE_API_PORT]), debug=True)
