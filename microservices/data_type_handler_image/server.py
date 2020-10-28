from flask import jsonify, Flask, request
import os
from data_type_handler import (
    MongoOperations,
    DataTypeHandlerRequestValidator,
    DataTypeConverter)

HTTP_STATUS_CODE_SUCESS = 200
HTTP_STATUS_CODE_SUCESS_CREATED = 201
HTTP_STATUS_CODE_NOT_ACCEPTABLE = 406
HTTP_STATUS_CODE_CONFLICT = 409

DATA_TYPE_HANDLER_HOST = "DATA_TYPE_HANDLER_HOST"
DATA_TYPE_HANDLER_PORT = "DATA_TYPE_HANDLER_PORT"

MESSAGE_RESULT = "result"

FILENAME_NAME = "filename"

FIRST_ARGUMENT = 0

MESSAGE_INVALID_URL = "invalid_url"
MESSAGE_DUPLICATE_FILE = "duplicate_file"
MESSAGE_CHANGED_FILE = "file_changed"
MESSAGE_DELETED_FILE = "deleted_file"

DATABASE_URL = "DATABASE_URL"
DATABASE_PORT = "DATABASE_PORT"
DATABASE_NAME = "DATABASE_NAME"
DATABASE_REPLICA_SET = "DATABASE_REPLICA_SET"

POST = "POST"
PATCH = "PATCH"

app = Flask(__name__)


def collection_database_url(database_url, database_name, database_filename,
                            database_replica_set):
    return database_url + '/' + \
           database_name + '.' + \
           database_filename + "?replicaSet=" + \
           database_replica_set + \
           "&authSource=admin"


@app.route('/fieldTypes/', methods=[PATCH])
def change_data_type():
    database = MongoOperations(
        os.environ[DATABASE_URL] + '/?replicaSet=' +
        os.environ[DATABASE_REPLICA_SET], os.environ[DATABASE_PORT],
        os.environ[DATABASE_NAME])

    request_validator = DataTypeHandlerRequestValidator(database)

    try:
        parent_filename = request.json["input_filename"]

        request_validator.filename_validator(parent_filename)
    except Exception as invalid_filename:
        return jsonify(
            {MESSAGE_RESULT:
                 invalid_filename.args[FIRST_ARGUMENT]}), \
               HTTP_STATUS_CODE_NOT_ACCEPTABLE

    try:
        request_validator.fields_validator(
            parent_filename, request.json)
    except Exception as invalid_fields:
        return jsonify(
            {MESSAGE_RESULT: invalid_fields.args[FIRST_ARGUMENT]}), \
               HTTP_STATUS_CODE_NOT_ACCEPTABLE

    data_type_converter = DataTypeConverter(database)
    data_type_converter.file_converter(
        parent_filename, request.json)

    return jsonify({MESSAGE_RESULT: MESSAGE_CHANGED_FILE}), \
           HTTP_STATUS_CODE_SUCESS


if __name__ == "__main__":
    app.run(host=os.environ[DATA_TYPE_HANDLER_HOST],
            port=int(os.environ[DATA_TYPE_HANDLER_PORT]))
