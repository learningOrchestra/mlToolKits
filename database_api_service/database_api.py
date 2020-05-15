import os
from flask import Flask
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
from bson import encode
from bson import decode
from flask import jsonify, request
import gridfs
from gridfs import GridFSBucket
import requests
import json

HTTP_STATUS_CODE_SUCESS = 200
HTTP_STATUS_CODE_SUCESS_CREATED = 201
HTTP_STATUS_CODE_NOT_FOUND = 404
HTTP_STATUS_CODE_SERVER_ERROR = 500
FILE_HANDLER_NAME = "response_handler"
MESSAGE_INVALID_URL = "invalid_url"
MESSAGE_RESULT = "result"
MESSAGE_CREATED_FILE = "file_created"
MESSAGE_FILENAME = "filename"
MESSAGE_DELETED_FILE = "deleted_file"
MESSAGE_INVALID_PARAMETER = "invalid_parameter"
CHUNK_SIZE = 1024

DATABASE_API_HOST = "DATABASE_API_HOST"
DATABASE_API_PORT = "DATABASE_API_PORT"
DATABASE_URL = "DATABASE_URL"
DATABASE_PORT = "DATABASE_PORT"

app = Flask(__name__)

mongo = MongoClient(os.environ[DATABASE_URL],
                    int(os.environ[DATABASE_PORT]))
files_gridfs = gridfs.GridFS(mongo.db)
files_bucket = GridFSBucket(mongo.db)


@app.route('/add', methods=['POST'])
def add_file():
    try:
        response = requests.get(request.json["url"], stream=True)

        if(response.status_code != HTTP_STATUS_CODE_SUCESS):
            return jsonify({MESSAGE_RESULT: MESSAGE_INVALID_URL}), \
                response.status_code
    except Exception:
        return jsonify({MESSAGE_RESULT: MESSAGE_INVALID_URL}), \
            HTTP_STATUS_CODE_SERVER_ERROR

    response_handler = open(FILE_HANDLER_NAME, "wb")

    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
        if chunk:
            response_handler.write(chunk)

    response_handler.close()
    response_file = open(FILE_HANDLER_NAME, "rb")

    file_stream = files_bucket.open_upload_stream(
                        request.json[MESSAGE_FILENAME],
                        chunk_size_bytes=CHUNK_SIZE,
                        metadata=request.json)

    file_stream.write(response_file)
    file_stream.close()
    response_file.close()

    return jsonify({MESSAGE_RESULT: MESSAGE_CREATED_FILE}), \
        HTTP_STATUS_CODE_SUCESS_CREATED


@app.route('/files')
def files():
    result = []
    for file in files_gridfs.find():
        result.append(json.loads(file.read()))

    return jsonify({MESSAGE_RESULT: result}), \
        HTTP_STATUS_CODE_SUCESS


@app.route('/file/<filename>',)
def file(filename):
    result = []
    for file in files_gridfs.find({MESSAGE_FILENAME: filename}):
        result.append(json.loads(file.read()))

    return jsonify({MESSAGE_RESULT: result}), \
        HTTP_STATUS_CODE_SUCESS


@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        file_id = files_gridfs.get_version(filename)._id
        files_gridfs.delete(file_id)
    except Exception:
        return jsonify({MESSAGE_RESULT: MESSAGE_INVALID_PARAMETER}), \
            HTTP_STATUS_CODE_SERVER_ERROR

    return jsonify({MESSAGE_RESULT: MESSAGE_DELETED_FILE}), \
        HTTP_STATUS_CODE_SUCESS


if __name__ == "__main__":
    app.run(host=os.environ[DATABASE_API_HOST],
            port=int(os.environ[DATABASE_API_PORT]))
