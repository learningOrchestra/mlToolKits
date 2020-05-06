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

app = Flask(__name__)
mongo = MongoClient(os.environ["DATABASE_URL"],
                    int(os.environ["DATABASE_PORT"]))
files_gridfs = gridfs.GridFS(mongo.db)


@app.route('/add', methods=['POST'])
def add_file():
    try:
        file_downloaded = requests.get(request.json["url"])

        if(file_downloaded.status_code != 200):
            response = jsonify({"stage": "download_file"})
            response.status_code = file_downloaded.status_code
            return response

        inserted_file = request.json
        inserted_file.update({"content": file_downloaded.json()})
        files_gridfs.put(encode(inserted_file),
                         filename=request.json["filename"])
        response = jsonify({"stage": "inserted_file"})
        response.status_code = 200
        return response

    except:
        response = jsonify({"stage": "unknow_error"})
        response.status_code = 500
        return response


@app.route('/files')
def files():
    result = []
    for files in files_gridfs.find():
        result.append(decode(files.read()))
    return dumps(result)


@app.route('/file/<filename>',)
def file(filename):
    try:
        result = []
        for files in files_gridfs.find({"filename": filename}):
            result.append(decode(files.read()))
        return dumps(result)

    except:
        return jsonify("File not found")


@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        file_id = files_gridfs.get_version(filename)._id
        files_gridfs.delete(file_id)
        response = jsonify('File deleted!')
        response.status_code = 200
        return response
    except:
        return jsonify("A error has ocurred in DELETE")


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0')
