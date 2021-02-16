from flask import jsonify, request, Flask, send_file
from database_execution import Parameters, Execution
from utils import (
    Database,
    UserRequest,
    ExploreStorage,
    TransformStorage,
    Metadata,
    Data)
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
explore_storage = ExploreStorage(database)
transform_storage = TransformStorage(database)


@app.route(Constants.MICROSERVICE_URI_PATH, methods=["POST"])
def create_execution() -> jsonify:
    service_type = request.args.get(Constants.TYPE_PARAM_NAME)
    tool_type = request.args.get(Constants.TOOL_PARAM_NAME)

    filename = request.json[Constants.NAME_FIELD_NAME]
    description = request.json[Constants.DESCRIPTION_FIELD_NAME]
    module_path = request.json[Constants.MODULE_PATH_FIELD_NAME]
    class_name = request.json[Constants.CLASS_FIELD_NAME]
    class_parameters = request.json[Constants.CLASS_PARAMETERS_FIELD_NAME]
    class_method_name = request.json[Constants.METHOD_FIELD_NAME]
    method_parameters = request.json[Constants.METHOD_PARAMETERS_FIELD_NAME]

    request_errors = analyse_post_request_errors(
        request_validator,
        filename,
        module_path,
        class_name,
        class_parameters,
        class_method_name,
        method_parameters
    )

    if request_errors is not None:
        return request_errors

    storage = None
    if service_type == Constants.EXPLORE_TYPE:
        storage = explore_storage
    elif service_type == Constants.TRANSFORM_TYPE:
        storage = transform_storage

    data = Data(database, storage)
    parameters = Parameters(database, data)
    metadata_creator = Metadata(database)

    execution = Execution(
        database,
        filename,
        service_type,
        storage,
        metadata_creator,
        module_path,
        class_name,
        class_parameters,
        parameters)

    execution.create(class_method_name, method_parameters, description)

    response_params = None
    if service_type == Constants.TRANSFORM_TYPE:
        response_params = Constants.MICROSERVICE_URI_GET_PARAMS

    return (
        jsonify({
            Constants.MESSAGE_RESULT:
                Constants.MICROSERVICE_URI_SWITCHER[service_type] +
                "/" +
                tool_type +
                "/" +
                filename +
                response_params}),
        Constants.HTTP_STATUS_CODE_SUCCESS_CREATED,
    )


@app.route(Constants.MICROSERVICE_URI_PATH + "/<filename>", methods=["PATCH"])
def update_execution(filename: str) -> jsonify:
    service_type = request.args.get(Constants.TYPE_PARAM_NAME)
    tool_type = request.args.get(Constants.TOOL_PARAM_NAME)
    description = request.json[Constants.DESCRIPTION_FIELD_NAME]
    class_method_name = request.json[Constants.METHOD_FIELD_NAME]
    method_parameters = request.json[Constants.METHOD_PARAMETERS_FIELD_NAME]

    storage = None
    if service_type == Constants.EXPLORE_TYPE:
        storage = explore_storage
    elif service_type == Constants.TRANSFORM_TYPE:
        storage = transform_storage

    data = Data(database, storage)

    request_errors = analyse_patch_request_errors(
        request_validator,
        data,
        filename,
        class_method_name,
        method_parameters)

    if request_errors is not None:
        return request_errors

    module_path, class_name = data.get_module_and_class(filename)
    class_parameters = data.get_class_parameters(filename)

    parameters = Parameters(database, data)
    metadata_creator = Metadata(database)

    execution = Execution(
        database,
        filename,
        service_type,
        storage,
        metadata_creator,
        module_path,
        class_name,
        class_parameters,
        parameters)

    execution.update(class_method_name, method_parameters, description)

    response_params = None
    if service_type == Constants.TRANSFORM_TYPE:
        response_params = Constants.MICROSERVICE_URI_GET_PARAMS

    return (
        jsonify({
            Constants.MESSAGE_RESULT:
                Constants.MICROSERVICE_URI_SWITCHER[service_type] +
                "/" +
                tool_type +
                "/" +
                filename +
                response_params}),
        Constants.HTTP_STATUS_CODE_SUCCESS_CREATED,
    )


@app.route(Constants.MICROSERVICE_URI_PATH + "/<filename>", methods=["GET"])
def get_image(filename):
    try:
        request_validator.existent_filename_validator(filename)

    except Exception as invalid_filename:
        return (
            jsonify(
                {Constants.MESSAGE_RESULT: str(invalid_filename)}),
            Constants.HTTP_STATUS_CODE_NOT_FOUND,
        )

    storage = explore_storage
    image = storage.read(filename)

    return send_file(image, mimetype="image/png")


@app.route(Constants.MICROSERVICE_URI_PATH + "/<filename>", methods=["DELETE"])
def delete_default_model(filename: str) -> jsonify:
    service_type = request.args.get(Constants.TYPE_PARAM_NAME)

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

    storage = None
    if service_type == Constants.EXPLORE_TYPE:
        storage = explore_storage
    elif service_type == Constants.TRANSFORM_TYPE:
        storage = transform_storage

    storage.delete(filename)

    return (
        jsonify({
            Constants.MESSAGE_RESULT: Constants.DELETED_MESSAGE}),
        Constants.HTTP_STATUS_CODE_SUCCESS,
    )


def analyse_post_request_errors(request_validator: UserRequest,
                                filename: str,
                                module_path: str,
                                class_name: str,
                                class_parameters: dict,
                                class_method: str,
                                method_parameters: dict) \
        -> Union[tuple, None]:
    try:
        request_validator.not_duplicated_filename_validator(
            filename
        )
    except Exception as duplicated_filename:
        return (
            jsonify({Constants.MESSAGE_RESULT: str(duplicated_filename)}),
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

    try:
        request_validator.valid_method_class_validator(
            module_path,
            class_name,
            class_method
        )
    except Exception as invalid_method_name:
        return (
            jsonify({Constants.MESSAGE_RESULT: str(invalid_method_name)}),
            Constants.HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    try:
        request_validator.valid_method_parameters_name_validator(
            module_path,
            class_name,
            class_method,
            method_parameters
        )
    except Exception as invalid_method_parameters:
        return (
            jsonify({Constants.MESSAGE_RESULT: str(invalid_method_parameters)}),
            Constants.HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    return None


def analyse_patch_request_errors(request_validator: UserRequest,
                                 data: Data,
                                 filename: str,
                                 class_method: str,
                                 method_parameters: dict) \
        -> Union[tuple, None]:
    try:
        request_validator.existent_filename_validator(
            filename
        )
    except Exception as nonexistent_train_filename:
        return (
            jsonify(
                {Constants.MESSAGE_RESULT: str(nonexistent_train_filename)}),
            Constants.HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    module_path, class_name = data.get_module_and_class(filename)

    try:
        request_validator.valid_method_class_validator(
            module_path,
            class_name,
            class_method
        )
    except Exception as invalid_method_name:
        return (
            jsonify({Constants.MESSAGE_RESULT: str(invalid_method_name)}),
            Constants.HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    try:
        request_validator.valid_method_parameters_name_validator(
            module_path,
            class_name,
            class_method,
            method_parameters
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
        host=os.environ["MICROSERVICE_IP"],
        port=int(os.environ["MICROSERVICE_PORT"])
    )
