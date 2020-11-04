from flask import jsonify, Flask, request
import os
from data_type_handler import (
    MongoOperations,
    DataTypeHandlerRequestValidator,
    DataTypeConverter,
    FileMetadataHandler)

HTTP_STATUS_CODE_SUCESS = 200
HTTP_STATUS_CODE_SUCESS_CREATED = 201
HTTP_STATUS_CODE_NOT_ACCEPTABLE = 406
HTTP_STATUS_CODE_CONFLICT = 409

DATA_TYPE_HANDLER_HOST = "DATA_TYPE_HANDLER_HOST"
DATA_TYPE_HANDLER_PORT = "DATA_TYPE_HANDLER_PORT"

MESSAGE_RESULT = "result"

FILENAME_NAME = "filename"
FIELD_TYPES_NAMES = "types"
PARENT_FILENAME_NAME = "input_filename"
FIRST_ARGUMENT = 0

MESSAGE_INVALID_URL = "invalid_url"
MESSAGE_DUPLICATE_FILE = "duplicate_file"
MESSAGE_DELETED_FILE = "deleted_file"

DATABASE_URL = "DATABASE_URL"
DATABASE_PORT = "DATABASE_PORT"
DATABASE_NAME = "DATABASE_NAME"
DATABASE_REPLICA_SET = "DATABASE_REPLICA_SET"

MICROSERVICE_URI_GET = "/api/learningOrchestra/v1/dataset/"
MICROSERVICE_URI_GET_PARAMS = "?query={}&limit=20&skip=0"

app = Flask(__name__)


@app.route('/fieldTypes', methods=["PATCH"])
def change_data_type():
    database = MongoOperations(
        os.environ[DATABASE_URL],
        os.environ[DATABASE_REPLICA_SET],
        os.environ[DATABASE_PORT],
        os.environ[DATABASE_NAME])

    request_validator = DataTypeHandlerRequestValidator(database)

    try:
        parent_filename = request.json[PARENT_FILENAME_NAME]

        request_validator.filename_validator(parent_filename)
    except Exception as invalid_filename:
        return jsonify(
            {MESSAGE_RESULT: invalid_filename.args[FIRST_ARGUMENT]}), \
               HTTP_STATUS_CODE_NOT_ACCEPTABLE

    try:
        request_validator.fields_validator(
            parent_filename, request.json[FIELD_TYPES_NAMES])
    except Exception as invalid_fields:
        return jsonify(
            {MESSAGE_RESULT: invalid_fields.args[FIRST_ARGUMENT]}), \
               HTTP_STATUS_CODE_NOT_ACCEPTABLE

    metadata_handler = FileMetadataHandler(database)
    data_type_converter = DataTypeConverter(database, metadata_handler)
    data_type_converter.convert_existent_file(
        parent_filename, request.json[FIELD_TYPES_NAMES])

    return jsonify({
        MESSAGE_RESULT:
            MICROSERVICE_URI_GET +
            request.json[PARENT_FILENAME_NAME] +
            MICROSERVICE_URI_GET_PARAMS}), HTTP_STATUS_CODE_SUCESS


if __name__ == "__main__":
    app.run(host=os.environ[DATA_TYPE_HANDLER_HOST],
            port=int(os.environ[DATA_TYPE_HANDLER_PORT]))
