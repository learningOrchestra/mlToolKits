import os
from flask import Flask
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
from bson import encode
from bson import decode
from flask import jsonify, request
import gridfs

app = Flask(__name__)
mongo = MongoClient(os.environ["DATABASE_URL"],
                    int(os.environ["DATABASE_PORT"]))
files_gridfs = gridfs.GridFS(mongo.db)


@app.route('/add', methods=['POST'])
def add_file():
    try:
        files_gridfs.put(encode(request.json),
                         filename=request.json["filename"])
        response = jsonify('file with filename = ' +
                           str(request.json["filename"]) + ' added!')
        response.status_code = 200
        return response
    except:
        return jsonify("A Error has ocurred, file not added!")


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
