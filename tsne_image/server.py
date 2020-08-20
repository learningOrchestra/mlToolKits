from flask import jsonify, request, Flask, send_file
import os
from tsne import (
    TsneGenerator,
    MongoOperations,
    TsneRequestValidator)

HTTP_STATUS_CODE_SUCESS = 200
HTTP_STATUS_CODE_SUCESS_CREATED = 201
HTTP_STATUS_CODE_CONFLICT = 409
HTTP_STATUS_CODE_NOT_ACCEPTABLE = 406
HTTP_STATUS_CODE_NOT_FOUND = 404

TSNE_HOST_IP = "TSNE_HOST_IP"
TSNE_HOST_PORT = "TSNE_HOST_PORT"

DATABASE_URL = "DATABASE_URL"
DATABASE_PORT = "DATABASE_PORT"
DATABASE_NAME = "DATABASE_NAME"
DATABASE_REPLICA_SET = "DATABASE_REPLICA_SET"

DOCUMENT_ID = '_id'
METADATA_DOCUMENT_ID = 0

GET = 'GET'
POST = 'POST'
DELETE = 'DELETE'

MESSAGE_RESULT = "result"
TSNE_FILENAME_NAME = "tsne_filename"
FIELDS_NAME = "fields"

MESSAGE_CREATED_FILE = "created_file"
MESSAGE_DELETED_FILE = "deleted_file"

FIRST_ARGUMENT = 0

app = Flask(__name__)


def collection_database_url(database_url, database_name, database_filename,
                            database_replica_set):
    return database_url + '/' + \
        database_name + '.' + \
        database_filename + "?replicaSet=" + \
        database_replica_set + \
        "&authSource=admin"


@app.route('/tsne/<parent_filename>', methods=[POST])
def create_tsne(parent_filename):
    database = MongoOperations(
        os.environ[DATABASE_URL] + '/?replicaSet=' +
        os.environ[DATABASE_REPLICA_SET], os.environ[DATABASE_PORT],
        os.environ[DATABASE_NAME])

    request_validator = TsneRequestValidator(database)

    try:
        request_validator.tsne_filename_validator(
            request.json[TSNE_FILENAME_NAME])
    except Exception as invalid_tsne_filename:
        return jsonify(
            {MESSAGE_RESULT:
                invalid_tsne_filename.args[FIRST_ARGUMENT]}),\
            HTTP_STATUS_CODE_CONFLICT

    try:
        request_validator.parent_filename_validator(
            parent_filename)
    except Exception as invalid_filename:
        return jsonify(
            {MESSAGE_RESULT: invalid_filename.args[FIRST_ARGUMENT]}),\
            HTTP_STATUS_CODE_NOT_ACCEPTABLE

    database_url_input = collection_database_url(
                            os.environ[DATABASE_URL],
                            os.environ[DATABASE_NAME],
                            parent_filename,
                            os.environ[DATABASE_REPLICA_SET])

    tsne_generator = TsneGenerator(
                            database_url_input)

    tsne_generator.create_image(
        parent_filename,
        request.json[TSNE_FILENAME_NAME])

    return jsonify(
        {MESSAGE_RESULT: MESSAGE_CREATED_FILE}),\
        HTTP_STATUS_CODE_SUCESS_CREATED


@app.route('/tsne', methods=[GET])
def get_images():
    images = os.listdir('.')
    return jsonify(
        {MESSAGE_RESULT: images}),\
        HTTP_STATUS_CODE_SUCESS


@app.route('/tsne/<filename>', methods=[GET])
def get_image(tsne_filename):
    filename = tsne_filename + '.png'
    return send_file(filename, mimetype='image/png')


@app.route('/tsne/<filename>', methods=[DELETE])
def delete_image(tsne_filename):
    os.remove(tsne_filename + ".png")
    return jsonify(
        {MESSAGE_RESULT: MESSAGE_DELETED_FILE}),\
        HTTP_STATUS_CODE_SUCESS

if __name__ == "__main__":
    app.run(host=os.environ[TSNE_HOST_IP],
            port=int(os.environ[TSNE_HOST_PORT]))
