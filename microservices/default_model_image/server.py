from flask import jsonify, request, Flask
import os
from default_model import DefaultModel
from utils import Database, UserRequest, Metadata
from typing import Union

HTTP_STATUS_CODE_SUCCESS = 200
HTTP_STATUS_CODE_SUCCESS_CREATED = 201
HTTP_STATUS_CODE_CONFLICT = 409
HTTP_STATUS_CODE_NOT_ACCEPTABLE = 406

DEFAULT_MODEL_HOST_IP = "DEFAULT_MODEL_HOST_IP"
DEFAULT_MODEL_HOST_PORT = "DEFAULT_MODEL_HOST_PORT"

DATABASE_URL = "DATABASE_URL"
DATABASE_PORT = "DATABASE_PORT"
DATABASE_NAME = "DATABASE_NAME"
DATABASE_REPLICA_SET = "DATABASE_REPLICA_SET"

DOCUMENT_ID = "_id"
METADATA_DOCUMENT_ID = 0

MESSAGE_RESULT = "result"

FUNCTION_PARAMETERS_NAME = "classParameters"

MICROSERVICE_URI_GET = "/api/learningOrchestra/v1/model/default/"
MICROSERVICE_URI_GET_PARAMS = "?query={}&limit=20&skip=0"

FIRST_ARGUMENT = 0

app = Flask(__name__)


@app.route("/defaultModel", methods=["POST"])
def create_default_model() -> jsonify:
    database_url = os.environ[DATABASE_URL]
    database_replica_set = os.environ[DATABASE_REPLICA_SET]
    database_name = os.environ[DATABASE_NAME]

    model_name = request.json["modelName"]
    description = request.json["description"]
    module_path = request.json["modulePath"]
    class_name = request.json["class"]
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

    description = request.json["description"]
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


@app.route("/defaultModel/tool", methods=["GET"])
def read_tools() -> jsonify:
    return (
        jsonify({
            MESSAGE_RESULT: DefaultModel.available_tools()}),
        HTTP_STATUS_CODE_SUCCESS,
    )


@app.route("/defaultModel/tool/<tool>/function", methods=["GET"])
def read_tool_functions(tool) -> jsonify:
    if tool not in DefaultModel.available_tools():
        return (
            jsonify({MESSAGE_RESULT: "tool doesn't available"}),
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
        package_name = module_path.split(".")[FIRST_ARGUMENT]
        request_validator.available_package_name_validator(
            package_name
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
                                 function_parameters: dict) \
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

    tool, function = get_model_tool_and_function(database, model_name)
    try:
        request_validator.valid_class_parameters_validator(
            tool,
            function,
            function_parameters
        )
    except Exception as invalid_function_parameters:
        return (
            jsonify({MESSAGE_RESULT: invalid_function_parameters.args[
                FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    return None


def get_model_tool_and_function(database: Database, model_name: str) -> tuple:
    metadata_document_query = {"_id": 0}
    model_metadata = database.find_one(model_name, metadata_document_query)
    tool = model_metadata["tool"]
    function = model_metadata["function"]

    return tool, function


if __name__ == "__main__":
    app.run(
        host=os.environ[DEFAULT_MODEL_HOST_IP],
        port=int(os.environ[DEFAULT_MODEL_HOST_PORT])
    )
