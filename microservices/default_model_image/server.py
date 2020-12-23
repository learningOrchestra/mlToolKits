from flask import jsonify, request, Flask
import os
from default_model import DefaultModel
from utils import Database, UserRequest, Metadata
from typing import Union
from constants import *

app = Flask(__name__)


@app.route("/defaultModel", methods=["POST"])
def create_default_model() -> jsonify:
    database_url = os.environ[DATABASE_URL]
    database_replica_set = os.environ[DATABASE_REPLICA_SET]
    database_name = os.environ[DATABASE_NAME]

    model_name = request.json[MODEL_FIELD_NAME]
    description = request.json[DESCRIPTION_FIELD_NAME]
    module_path = request.json[MODULE_PATH_FIELD_NAME]
    class_name = request.json[CLASS_FIELD_NAME]
    class_parameters = request.json[FUNCTION_PARAMETERS_NAME]

    database = Database(
        database_url,
        database_replica_set,
        int(os.environ[DATABASE_PORT]),
        database_name,
    )

    request_validator = UserRequest(database)

    request_errors = analyse_post_request_errors(
        request_validator,
        model_name,
        module_path,
        class_name,
        class_parameters)

    if request_errors is not None:
        return request_errors

    metadata_creator = Metadata(database)
    default_model = DefaultModel(metadata_creator, database)

    default_model.create(
        model_name, module_path, class_name, description, class_parameters)

    return (
        jsonify({
            MESSAGE_RESULT:
                MICROSERVICE_URI_GET +
                model_name +
                MICROSERVICE_URI_GET_PARAMS}),
        HTTP_STATUS_CODE_SUCCESS_CREATED,
    )


@app.route("/defaultModel/<model_name>", methods=["PATCH"])
def update_default_model(model_name: str) -> jsonify:
    database_url = os.environ[DATABASE_URL]
    database_replica_set = os.environ[DATABASE_REPLICA_SET]
    database_name = os.environ[DATABASE_NAME]

    database = Database(
        database_url,
        database_replica_set,
        int(os.environ[DATABASE_PORT]),
        database_name,
    )

    description = request.json[DESCRIPTION_FIELD_NAME]
    function_parameters = request.json[FUNCTION_PARAMETERS_NAME]

    request_validator = UserRequest(database)

    request_errors = analyse_patch_request_errors(
        request_validator,
        database,
        model_name,
        function_parameters)

    if request_errors is not None:
        return request_errors

    tool, function = get_model_tool_and_function(database, model_name)

    metadata_creator = Metadata(database)
    default_model = DefaultModel(metadata_creator, database)

    default_model.update(
        model_name, tool, function, description, function_parameters)

    return (
        jsonify({
            MESSAGE_RESULT:
                MICROSERVICE_URI_GET +
                model_name +
                MICROSERVICE_URI_GET_PARAMS}),
        HTTP_STATUS_CODE_SUCCESS_CREATED,
    )


@app.route("/defaultModel/tool", methods=[GET_METHOD_NAME])
def read_tools() -> jsonify:
    return (
        jsonify({
            MESSAGE_RESULT: DefaultModel.available_tools()}),
        HTTP_STATUS_CODE_SUCCESS,
    )


@app.route("/defaultModel/tool/<tool>/detail", methods=[GET_METHOD_NAME])
def read_tool_functions(tool) -> jsonify:
    if tool not in DefaultModel.available_tools():
        return (
            jsonify({MESSAGE_RESULT: "Package doesn't available"}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    return (
        jsonify({
            MESSAGE_RESULT: help(tool)}),
        HTTP_STATUS_CODE_SUCCESS,
    )


def analyse_post_request_errors(request_validator: UserRequest,
                                model_name: str,
                                module_path: str,
                                class_name: str,
                                class_parameters: dict) \
        -> Union[tuple, None]:
    try:
        request_validator.not_duplicated_filename_validator(
            model_name
        )
    except Exception as duplicated_model_filename:
        return (
            jsonify({MESSAGE_RESULT: duplicated_model_filename.args[
                FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_CONFLICT,
        )

    try:
        request_validator.available_module_path_validator(
            module_path
        )
    except Exception as invalid_tool_name:
        return (
            jsonify({MESSAGE_RESULT: invalid_tool_name.args[
                FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    try:
        request_validator.valid_class_validator(
            module_path,
            class_name
        )
    except Exception as invalid_function_name:
        return (
            jsonify({MESSAGE_RESULT: invalid_function_name.args[
                FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    try:
        request_validator.valid_class_parameters_validator(
            module_path,
            class_name,
            class_parameters
        )
    except Exception as invalid_function_parameters:
        return (
            jsonify({MESSAGE_RESULT: invalid_function_parameters.args[
                FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    return None


def analyse_patch_request_errors(request_validator: UserRequest,
                                 database: Database,
                                 model_name: str,
                                 class_parameters: dict) \
        -> Union[tuple, None]:
    try:
        request_validator.not_duplicated_filename_validator(
            model_name
        )
    except Exception as duplicated_model_filename:
        return (
            jsonify({MESSAGE_RESULT: duplicated_model_filename.args[
                FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_CONFLICT,
        )

    module_path, class_name = get_model_tool_and_function(database, model_name)
    try:
        request_validator.valid_class_parameters_validator(
            module_path,
            class_name,
            class_parameters
        )
    except Exception as invalid_function_parameters:
        return (
            jsonify({MESSAGE_RESULT: invalid_function_parameters.args[
                FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    return None


def get_model_tool_and_function(database: Database, model_name: str) -> tuple:
    metadata_document_query = {ID_FIELD_NAME: METADATA_DOCUMENT_ID}
    model_metadata = database.find_one(model_name, metadata_document_query)
    module_path = model_metadata[MODULE_PATH_FIELD_NAME]
    class_name = model_metadata[CLASS_FIELD_NAME]

    return module_path, class_name


if __name__ == "__main__":
    app.run(
        host=os.environ[DEFAULT_MODEL_HOST_IP],
        port=int(os.environ[DEFAULT_MODEL_HOST_PORT])
    )
