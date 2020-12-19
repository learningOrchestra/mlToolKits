from flask import jsonify, request, Flask
import os
from default_model import DefaultModel
from default_model_utils import Database, UserRequest, Metadata

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

FUNCTION_PARAMETERS_NAME = "functionParameters"

MICROSERVICE_URI_GET = "/api/learningOrchestra/v1/model/default/"
MICROSERVICE_URI_GET_PARAMS = "?query={}&limit=20&skip=0"

FIRST_ARGUMENT = 0

app = Flask(__name__)


@app.route("/defaultModel", methods=["POST"])
def create_default_model():
    database_url = os.environ[DATABASE_URL]
    database_replica_set = os.environ[DATABASE_REPLICA_SET]
    database_name = os.environ[DATABASE_NAME]

    model_name = request.json["model_name"]
    description = request.json["description"]
    tool = request.json["tool"]
    function = request.json["function"]
    function_parameters = request.json[FUNCTION_PARAMETERS_NAME]

    database = Database(
        database_url,
        database_replica_set,
        os.environ[DATABASE_PORT],
        database_name,
    )

    request_validator = UserRequest(database)

    request_errors = analyse_request_errors(
        request_validator,
        model_name,
        tool,
        function,
        function_parameters)

    if request_errors is not None:
        return request_errors

    metadata_creator = Metadata(database)
    default_model = DefaultModel(metadata_creator)

    default_model.create(
        model_name, tool, function, description, function_parameters)

    return (
        jsonify({
            MESSAGE_RESULT:
                MICROSERVICE_URI_GET +
                model_name +
                MICROSERVICE_URI_GET_PARAMS}),
        HTTP_STATUS_CODE_SUCCESS_CREATED,
    )


@app.route("/defaultModel", methods=["PATCH"])
def update_default_model():
    pass


@app.route("/defaultModel/tool", methods=["GET"])
def read_tools():
    pass


@app.route("/defaultModel/tool/<tool>", methods=["GET"])
def read_tool_functions(tool):
    pass


def analyse_request_errors(request_validator,
                           model_name,
                           tool_name,
                           function_name,
                           function_parameters):
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
        request_validator.available_tool_name_validator(
            tool_name
        )
    except Exception as invalid_tool_name:
        return (
            jsonify({MESSAGE_RESULT: invalid_tool_name.args[
                FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    try:
        request_validator.valid_function_validator(
            function_name
        )
    except Exception as invalid_function_name:
        return (
            jsonify({MESSAGE_RESULT: invalid_function_name.args[
                FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    try:
        request_validator.valid_function_parameters_validator(
            function_parameters
        )
    except Exception as invalid_function_parameters:
        return (
            jsonify({MESSAGE_RESULT: invalid_function_parameters.args[
                FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    return None


if __name__ == "__main__":
    app.run(
        host=os.environ[DEFAULT_MODEL_HOST_IP],
        port=int(os.environ[DEFAULT_MODEL_HOST_PORT])
    )
