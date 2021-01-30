from flask import jsonify, request, Flask
from default_model import DefaultModel
from utils import *
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
    storage = ModelStorage(database)
    default_model = DefaultModel(
        database,
        model_name,
        metadata_creator,
        module_path,
        class_name,
        storage)

    default_model.create(
        description, class_parameters)

    return (
        jsonify({
            MESSAGE_RESULT:
                MICROSERVICE_URI_GET +
                model_name +
                MICROSERVICE_URI_GET_PARAMS}),
        HTTP_STATUS_CODE_SUCCESS_CREATED,
    )


@app.route("/defaultModel/<filename>", methods=["PATCH"])
def update_default_model(filename: str) -> jsonify:
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

    data = Data(database)

    request_errors = analyse_patch_request_errors(
        request_validator,
        data,
        filename,
        function_parameters)

    if request_errors is not None:
        return request_errors

    module_path, class_name = data.get_module_and_class_from_a_model(filename)

    metadata_creator = Metadata(database)
    storage = ModelStorage(database)
    default_model = DefaultModel(
        database,
        filename,
        metadata_creator,
        module_path,
        class_name,
        storage)

    default_model.update(
        description, function_parameters)

    return (
        jsonify({
            MESSAGE_RESULT:
                MICROSERVICE_URI_GET +
                filename +
                MICROSERVICE_URI_GET_PARAMS}),
        HTTP_STATUS_CODE_SUCCESS_CREATED,
    )


@app.route("/defaultModel/<filename>", methods=["DELETE"])
def delete_default_model(filename: str) -> jsonify:
    database_url = os.environ[DATABASE_URL]
    database_replica_set = os.environ[DATABASE_REPLICA_SET]
    database_name = os.environ[DATABASE_NAME]

    database = Database(
        database_url,
        database_replica_set,
        int(os.environ[DATABASE_PORT]),
        database_name,
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

    storage = ModelStorage(database)
    storage.delete(filename)

    return (
        jsonify({
            MESSAGE_RESULT: DELETED_MESSAGE}),
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
            jsonify({MESSAGE_RESULT: str(duplicated_model_filename)}),
            HTTP_STATUS_CODE_CONFLICT,
        )

    try:
        request_validator.available_module_path_validator(
            module_path
        )
    except Exception as invalid_tool_name:
        return (
            jsonify({MESSAGE_RESULT: str(invalid_tool_name)}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    try:
        request_validator.valid_class_validator(
            module_path,
            class_name
        )
    except Exception as invalid_function_name:
        return (
            jsonify({MESSAGE_RESULT: str(invalid_function_name)}),
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
            jsonify({MESSAGE_RESULT: str(invalid_function_parameters)}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    return None


def analyse_patch_request_errors(request_validator: UserRequest,
                                 data: Data,
                                 model_name: str,
                                 class_parameters: dict) \
        -> Union[tuple, None]:
    try:
        request_validator.existent_filename_validator(
            model_name
        )
    except Exception as nonexistent_model_filename:
        return (
            jsonify({MESSAGE_RESULT: str(nonexistent_model_filename)}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    module_path, class_name = data.get_module_and_class_from_a_model(
        model_name)
    try:
        request_validator.valid_class_parameters_validator(
            module_path,
            class_name,
            class_parameters
        )
    except Exception as invalid_function_parameters:
        return (
            jsonify({MESSAGE_RESULT: str(invalid_function_parameters)}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    return None


if __name__ == "__main__":
    app.run(
        host=os.environ[DEFAULT_MODEL_HOST_IP],
        port=int(os.environ[DEFAULT_MODEL_HOST_PORT])
    )