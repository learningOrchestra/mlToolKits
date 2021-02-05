from flask import jsonify, request, Flask
from code_execution import *
from utils import *
from typing import Union
from constants import *

app = Flask(__name__)

DATABASE_URL = os.environ[DATABASE_URL]
DATABASE_REPLICA_SET = os.environ[DATABASE_REPLICA_SET]
DATABASE_NAME = os.environ[DATABASE_NAME]


@app.route(MICROSERVICE_URI_PATH, methods=["POST"])
def create_execution() -> jsonify:
    filename = request.json[NAME_FIELD_NAME]
    description = request.json[DESCRIPTION_FIELD_NAME]
    service_type = request.args.get(TYPE_PARAM_NAME)
    function_parameters = request.json[FUNCTION_PARAMETERS_FIELD_NAME]
    function = request.json[FUNCTION_FIELD_NAME]

    database = Database(
        DATABASE_URL,
        DATABASE_REPLICA_SET,
        int(os.environ[DATABASE_PORT]),
        DATABASE_NAME,
    )

    request_validator = UserRequest(database)

    request_errors = analyse_post_request_errors(
        request_validator,
        filename
    )

    if request_errors is not None:
        return request_errors

    metadata_creator = Metadata(database)
    storage = ObjectStorage(database)
    data = Data(database, storage)
    parameters = Parameters(database, data)

    execution = Execution(
        database,
        filename,
        service_type,
        storage,
        metadata_creator,
        parameters)

    execution.create(function, function_parameters, description)

    return (
        jsonify({
            MESSAGE_RESULT:
                MICROSERVICE_URI_SWITCHER[service_type] +
                "/" +
                filename +
                MICROSERVICE_URI_GET_PARAMS}),
        HTTP_STATUS_CODE_SUCCESS_CREATED,
    )


@app.route(MICROSERVICE_URI_PATH + "/<filename>", methods=["PATCH"])
def update_execution(filename: str) -> jsonify:
    service_type = request.args.get(TYPE_PARAM_NAME)

    database = Database(
        DATABASE_URL,
        DATABASE_REPLICA_SET,
        int(os.environ[DATABASE_PORT]),
        DATABASE_NAME,
    )

    description = request.json[DESCRIPTION_FIELD_NAME]
    function = request.json[FUNCTION_FIELD_NAME]
    function_parameters = request.json[FUNCTION_PARAMETERS_FIELD_NAME]

    request_validator = UserRequest(database)
    request_errors = analyse_patch_request_errors(
        request_validator,
        filename)

    if request_errors is not None:
        return request_errors

    metadata_creator = Metadata(database)
    storage = ObjectStorage(database)
    data = Data(database, storage)
    parameters = Parameters(database, data)

    execution = Execution(
        database,
        filename,
        service_type,
        storage,
        metadata_creator,
        parameters)

    execution.update(function, function_parameters, description)

    return (
        jsonify({
            MESSAGE_RESULT:
                MICROSERVICE_URI_SWITCHER[service_type] +
                "/" +
                filename +
                MICROSERVICE_URI_GET_PARAMS}),
        HTTP_STATUS_CODE_SUCCESS_CREATED,
    )


@app.route(MICROSERVICE_URI_PATH + "/<filename>", methods=["DELETE"])
def delete_default_model(filename: str) -> jsonify:
    database = Database(
        DATABASE_URL,
        DATABASE_REPLICA_SET,
        int(os.environ[DATABASE_PORT]),
        DATABASE_NAME,
    )

    request_validator = UserRequest(database)

    try:
        request_validator.existent_filename_validator(
            filename
        )
    except Exception as nonexistent_model_filename:
        return (
            jsonify({MESSAGE_RESULT: str(nonexistent_model_filename)}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    storage = ObjectStorage(database)
    storage.delete(filename)

    return (
        jsonify({
            MESSAGE_RESULT: DELETED_MESSAGE}),
        HTTP_STATUS_CODE_SUCCESS,
    )


def analyse_post_request_errors(request_validator: UserRequest,
                                filename: str) \
        -> Union[tuple, None]:
    try:
        request_validator.not_duplicated_filename_validator(
            filename
        )
    except Exception as duplicated_filename:
        return (
            jsonify({MESSAGE_RESULT: str(duplicated_filename)}),
            HTTP_STATUS_CODE_CONFLICT,
        )

    return None


def analyse_patch_request_errors(request_validator: UserRequest,
                                 filename: str) \
        -> Union[tuple, None]:
    try:
        request_validator.existent_filename_validator(
            filename
        )
    except Exception as nonexistent_train_filename:
        return (
            jsonify({MESSAGE_RESULT: str(nonexistent_train_filename)}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    return None


if __name__ == "__main__":
    app.run(
        host=os.environ["MICROSERVICE_IP"],
        port=int(os.environ["MICROSERVICE_PORT"])
    )
