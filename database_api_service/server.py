from flask import jsonify, request, Flask
import os
from database_api import DatabaseApi

HTTP_STATUS_CODE_SUCESS = 200
HTTP_STATUS_CODE_SUCESS_CREATED = 201
HTTP_STATUS_CODE_SERVER_ERROR = 500

DATABASE_API_HOST = "DATABASE_API_HOST"
DATABASE_API_PORT = "DATABASE_API_PORT"

MESSAGE_RESULT = "result"

app = Flask(__name__)

database = DatabaseApi()


@app.route('/add', methods=['POST'])
def add_file():
    result = database.add_file(request.json["url"], request.json["filename"])

    if(result == DatabaseApi.MESSAGE_INVALID_URL):
        return jsonify({MESSAGE_RESULT: DatabaseApi.MESSAGE_INVALID_URL}), \
            HTTP_STATUS_CODE_SERVER_ERROR

    elif(result == DatabaseApi.MESSAGE_DUPLICATE_FILE):
        return jsonify({MESSAGE_RESULT: DatabaseApi.MESSAGE_DUPLICATE_FILE}), \
            HTTP_STATUS_CODE_SERVER_ERROR

    else:
        return jsonify({MESSAGE_RESULT: DatabaseApi.MESSAGE_CREATED_FILE}), \
            HTTP_STATUS_CODE_SUCESS_CREATED


@app.route('/file', methods=['POST'])
def read_file():
    file_result = database.read_file(
        request.json['filename'], request.json['skip'],
        request.json['limit'], request.json['query'])

    return jsonify({MESSAGE_RESULT: file_result}), \
        HTTP_STATUS_CODE_SUCESS


@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    result = database.delete_file(filename)

    if(result == DatabaseApi.MESSAGE_DELETED_FILE):
        return jsonify({MESSAGE_RESULT: DatabaseApi.MESSAGE_DELETED_FILE}), \
            HTTP_STATUS_CODE_SUCESS


@app.route('/files')
def get_files():
    return jsonify({MESSAGE_RESULT: database.get_files()}), \
            HTTP_STATUS_CODE_SUCESS


if __name__ == "__main__":
    app.run(host=os.environ[DATABASE_API_HOST],
            port=int(os.environ[DATABASE_API_PORT]))
