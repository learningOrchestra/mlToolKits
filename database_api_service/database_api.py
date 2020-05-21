import os
from flask import Flask
from pymongo import MongoClient, errors
from bson.json_util import loads, dumps
from flask import jsonify, request
import requests
from contextlib import closing
import csv
import json 
import codecs

HTTP_STATUS_CODE_SUCESS = 200
HTTP_STATUS_CODE_SUCESS_CREATED = 201
HTTP_STATUS_CODE_SERVER_ERROR = 500
MESSAGE_INVALID_URL = "invalid_url"
MESSAGE_DUPLICATE_FILE = "duplicate_file"
MESSAGE_RESULT = "result"
MESSAGE_CREATED_FILE = "file_created"
MESSAGE_FILENAME = "filename"
MESSAGE_DELETED_FILE = "deleted_file"
UTF8 = "utf-8"
DATABASE_API_HOST = "DATABASE_API_HOST"
DATABASE_API_PORT = "DATABASE_API_PORT"
DATABASE_URL = "DATABASE_URL"
DATABASE_PORT = "DATABASE_PORT"

app = Flask(__name__)

mongo_client = MongoClient(os.environ[DATABASE_URL],
                           int(os.environ[DATABASE_PORT]))
database = mongo_client.database


@app.route('/add', methods=['POST'])
def add_file():
    result = []
    try:
        with closing(requests.get(request.json['url'], stream=True)) as r:
            reader = csv.reader(
                codecs.iterdecode(r.iter_lines(), encoding=UTF8),
                delimiter=',', quotechar='"')
            count = 1
            file_collection = database[request.json[MESSAGE_FILENAME]]
            headers = next(reader)
            for row in reader:
                json_object = {headers[i]: row[i] for i in range(len(headers))}
                json_object["_id"] = count
                file_collection.insert_one(json_object)
                count += 1

    except requests.exceptions.RequestException:
        return jsonify({MESSAGE_RESULT: MESSAGE_INVALID_URL}), \
            HTTP_STATUS_CODE_SERVER_ERROR

    except errors.PyMongoError:
        return jsonify({MESSAGE_RESULT: MESSAGE_DUPLICATE_FILE}), \
            HTTP_STATUS_CODE_SERVER_ERROR

    return jsonify({MESSAGE_RESULT: MESSAGE_CREATED_FILE}), \
        HTTP_STATUS_CODE_SUCESS_CREATED


@app.route('/file', methods=['POST'])
def file():
    result = []
    file_collection = database[request.json['filename']]

    skip = request.json['skip']
    limit = request.json['limit']
    query = request.get_json()['query']

    for file in file_collection.find(query).skip(skip).limit(limit):
        result.append(json.loads(dumps(file)))

    return jsonify({MESSAGE_RESULT: result}), \
        HTTP_STATUS_CODE_SUCESS


@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    file_collection = database[filename]
    file_collection.drop()

    return jsonify({MESSAGE_RESULT: MESSAGE_DELETED_FILE}), \
        HTTP_STATUS_CODE_SUCESS


if __name__ == "__main__":
    app.run(host=os.environ[DATABASE_API_HOST],
            port=int(os.environ[DATABASE_API_PORT]))
