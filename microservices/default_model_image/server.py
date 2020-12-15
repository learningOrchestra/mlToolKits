from flask import jsonify, request, Flask
import os
from default_model import DefaultModel
from utils import Database, UserRequest, Metadata

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
        function)

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
                           model_name_filename,
                           model_tool,
                           model_tool_function):
    try:
        request_validator.projection_filename_validator(
            model_name_filename
        )
    except Exception as invalid_projection_filename:
        return (
            jsonify({MESSAGE_RESULT: invalid_projection_filename.args[
                FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_CONFLICT,
        )

    return None


if __name__ == "__main__":
    app.run(
        host=os.environ[DEFAULT_MODEL_HOST_IP],
        port=int(os.environ[DEFAULT_MODEL_HOST_PORT])
    )
