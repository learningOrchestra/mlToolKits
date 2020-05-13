import os
from flask import Flask
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
from bson import encode
from bson import decode
from flask import jsonify, request
import gridfs
import requests
import json

http_status_code_success = 200
http_status_code_sucess_created = 201
http_status_code_not_found = 404
http_status_code_server_error = 500
file_handler_name = "response_handler"

app = Flask(__name__)

mongo = MongoClient(os.environ["DATABASE_URL"],
                    int(os.environ["DATABASE_PORT"]))
files_gridfs = gridfs.GridFS(mongo.db)


@app.route('/add', methods=['POST'])
def add_file():
    global http_status_code_sucess_created, http_status_code_success

    try:
        response = requests.get(request.json["url"], stream=True)
        if(response.status_code != http_status_code_success):
            return jsonify("invalid_url"), response.status_code
    except Exception:
        return jsonify("invalid_url"), http_status_code_server_error

    response_handler = open(file_handler_name, "wb")

    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            response_handler.write(chunk)

    response_handler.close()
    response_file = open(file_handler_name, "rb")
    inserted_file = request.json

    inserted_file.update({"content": json.loads(response_file.read())})
    files_gridfs.put(encode(inserted_file),
                     filename=request.json["filename"])

    response_file.close()
    os.remove(file_handler_name)

    return jsonify("file_created"), http_status_code_sucess_created


@app.route('/files')
def files():
    global http_status_code_success

    result = []
    for files in files_gridfs.find():
        result.append(decode(files.read()))

    return dumps(result), http_status_code_success


@app.route('/file/<filename>',)
def file(filename):
    global http_status_code_success

    result = []
    for files in files_gridfs.find({"filename": filename}):
        result.append(decode(files.read()))

    return dumps(result), http_status_code_success


@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    global http_status_code_success

    file_id = files_gridfs.get_version(filename)._id
    files_gridfs.delete(file_id)

    return jsonify("file_deleted"), http_status_code_success


@app.errorhandler(http_status_code_not_found)
def not_found(error=None):
    global http_status_code_not_found
    return jsonify('not_found: ' + request.url), http_status_code_not_found


if __name__ == "__main__":
    app.run(host=os.environ["DATABASE_API_HOST"],
            port=int(os.environ["DATABASE_API_PORT"]))
