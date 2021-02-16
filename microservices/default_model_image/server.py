from flask import jsonify, request, Flask
from default_model import DefaultModel
from utils import Database, UserRequest, Metadata, ObjectStorage, Data
import os
from typing import Union
from constants import Constants

app = Flask(__name__)

database = Database(
    os.environ[Constants.DATABASE_URL],
    os.environ[Constants.DATABASE_REPLICA_SET],
    int(os.environ[Constants.DATABASE_PORT]),
    os.environ[Constants.DATABASE_NAME],
)

request_validator = UserRequest(database)
storage = ObjectStorage(database)
data = Data(database)


@app.route("/defaultModel", methods=["POST"])
def create_default_model() -> jsonify:
    model_name = request.json[Constants.MODEL_FIELD_NAME]
    description = request.json[Constants.DESCRIPTION_FIELD_NAME]
    module_path = request.json[Constants.MODULE_PATH_FIELD_NAME]
    class_name = request.json[Constants.CLASS_FIELD_NAME]
    class_parameters = request.json[Constants.FUNCTION_PARAMETERS_NAME]

    request_errors = analyse_post_request_errors(
        request_validator,
        model_name,
        module_path,
        class_name,
        class_parameters)

    if request_errors is not None:
        return request_errors

    metadata_creator = Metadata(database)

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
            Constants.MESSAGE_RESULT:
                Constants.MICROSERVICE_URI_GET +
                model_name +
                Constants.MICROSERVICE_URI_GET_PARAMS}),
        Constants.HTTP_STATUS_CODE_SUCCESS_CREATED,
    )


@app.route("/defaultModel/<filename>", methods=["PATCH"])
def update_default_model(filename: str) -> jsonify:
    description = request.json[Constants.DESCRIPTION_FIELD_NAME]
    function_parameters = request.json[Constants.FUNCTION_PARAMETERS_NAME]

    request_errors = analyse_patch_request_errors(
        request_validator,
        data,
        filename,
        function_parameters)

    if request_errors is not None:
        return request_errors

    module_path, class_name = data.get_module_and_class_from_a_model(filename)

    metadata_creator = Metadata(database)

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
            Constants.MESSAGE_RESULT:
                Constants.MICROSERVICE_URI_GET +
                filename +
                Constants.MICROSERVICE_URI_GET_PARAMS}),
        Constants.HTTP_STATUS_CODE_SUCCESS_CREATED,
    )


@app.route("/defaultModel/<filename>", methods=["DELETE"])
def delete_default_model(filename: str) -> jsonify:
    try:
        request_validator.existent_filename_validator(
            filename
        )
    except Exception as nonexistent_model_filename:
        return (
            jsonify(
                {Constants.MESSAGE_RESULT: str(nonexistent_model_filename)}),
            Constants.HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    storage.delete(filename)

    return (
        jsonify({
            Constants.MESSAGE_RESULT: Constants.DELETED_MESSAGE}),
        Constants.HTTP_STATUS_CODE_SUCCESS,
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
            jsonify({Constants.MESSAGE_RESULT: str(duplicated_model_filename)}),
            Constants.HTTP_STATUS_CODE_CONFLICT,
        )

    try:
        request_validator.available_module_path_validator(
            module_path
        )
    except Exception as invalid_tool_name:
        return (
            jsonify({Constants.MESSAGE_RESULT: str(invalid_tool_name)}),
            Constants.HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    try:
        request_validator.valid_class_validator(
            module_path,
            class_name
        )
    except Exception as invalid_function_name:
        return (
            jsonify({Constants.MESSAGE_RESULT: str(invalid_function_name)}),
            Constants.HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    try:
        request_validator.valid_class_parameters_validator(
            module_path,
            class_name,
            class_parameters
        )
    except Exception as invalid_function_parameters:
        return (
            jsonify(
                {Constants.MESSAGE_RESULT: str(invalid_function_parameters)}),
            Constants.HTTP_STATUS_CODE_NOT_ACCEPTABLE,
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
            jsonify(
                {Constants.MESSAGE_RESULT: str(nonexistent_model_filename)}),
            Constants.HTTP_STATUS_CODE_NOT_ACCEPTABLE,
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
            jsonify(
                {Constants.MESSAGE_RESULT: str(invalid_function_parameters)}),
            Constants.HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    return None


if __name__ == "__main__":
    app.run(
        host=os.environ[Constants.DEFAULT_MODEL_HOST_IP],
        port=int(os.environ[Constants.DEFAULT_MODEL_HOST_PORT])
    )
