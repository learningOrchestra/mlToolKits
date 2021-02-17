from flask import jsonify, request, Flask
import os
from binary_execution import Execution, Parameters
from utils import UserRequest, Database, ObjectStorage, Data, Metadata
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
data = Data(database, storage)
metadata_creator = Metadata(database)
parameters_handler = Parameters(database, data)


@app.route(Constants.MICROSERVICE_URI_PATH, methods=["POST"])
def create_execution() -> jsonify:
    service_type = request.args.get(Constants.TYPE_FIELD_NAME)

    parent_name = request.json[Constants.PARENT_NAME_FIELD_NAME]
    filename = request.json[Constants.NAME_FIELD_NAME]
    description = request.json[Constants.DESCRIPTION_FIELD_NAME]
    class_method = request.json[Constants.METHOD_FIELD_NAME]
    method_parameters = request.json[Constants.METHOD_PARAMETERS_FIELD_NAME]

    request_errors = analyse_post_request_errors(
        request_validator,
        data,
        filename,
        parent_name,
        class_method,
        method_parameters)

    if request_errors is not None:
        return request_errors

    parent_name_service_type = data.get_type(parent_name)

    train_model = Execution(
        database,
        filename,
        service_type,
        parent_name,
        parent_name_service_type,
        metadata_creator,
        class_method,
        parameters_handler,
        storage
    )

    module_path, class_name = data.get_module_and_class_from_a_model(
        parent_name)
    train_model.create(
        module_path, class_name, method_parameters, description)

    return (
        jsonify({
            Constants.MESSAGE_RESULT:
                f'{Constants.MICROSERVICE_URI_SWITCHER[service_type]}'
                f'{filename}{Constants.MICROSERVICE_URI_GET_PARAMS}'}),
        Constants.HTTP_STATUS_CODE_SUCCESS_CREATED,
    )


@app.route(f'{Constants.MICROSERVICE_URI_PATH}/<filename>', methods=["PATCH"])
def update_execution(filename: str) -> jsonify:
    service_type = request.args.get(Constants.TYPE_FIELD_NAME)
    description = request.json[Constants.DESCRIPTION_FIELD_NAME]
    method_parameters = request.json[Constants.METHOD_PARAMETERS_FIELD_NAME]

    request_errors = analyse_patch_request_errors(
        request_validator,
        data,
        filename,
        method_parameters)

    if request_errors is not None:
        return request_errors

    module_path, function = data.get_module_and_class_from_a_model(
        filename)
    model_name = data.get_model_name_from_a_child(filename)
    method_name = data.get_class_method_from_a_executor_name(filename)

    parent_name_service_type = data.get_type(model_name)

    default_model = Execution(
        database,
        filename,
        service_type,
        model_name,
        parent_name_service_type,
        metadata_creator,
        method_name,
        parameters_handler,
        storage)

    default_model.update(
        module_path, method_parameters, description)

    return (
        jsonify({
            Constants.MESSAGE_RESULT:
                f'{Constants.MICROSERVICE_URI_SWITCHER[service_type]}'
                f'{filename}{Constants.MICROSERVICE_URI_GET_PARAMS}'}),
        Constants.HTTP_STATUS_CODE_SUCCESS_CREATED,
    )


@app.route(f'{Constants.MICROSERVICE_URI_PATH}/<filename>', methods=["DELETE"])
def delete_default_model(filename: str) -> jsonify:
    service_type = request.args.get(Constants.TYPE_FIELD_NAME)

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

    storage.delete(filename, service_type)

    return (
        jsonify({
            Constants.MESSAGE_RESULT: Constants.DELETED_MESSAGE}),
        Constants.HTTP_STATUS_CODE_SUCCESS,
    )


def analyse_post_request_errors(request_validator: UserRequest,
                                data: Data,
                                filename: str,
                                parent_name: str,
                                class_method: str,
                                method_parameters: dict) \
        -> Union[tuple, None]:
    try:
        request_validator.not_duplicated_filename_validator(
            filename
        )
    except Exception as duplicated_train_filename:
        return (
            jsonify({Constants.MESSAGE_RESULT: str(duplicated_train_filename)}),
            Constants.HTTP_STATUS_CODE_CONFLICT,
        )

    try:
        request_validator.existent_filename_validator(
            parent_name
        )
    except Exception as invalid_model_name:
        return (
            jsonify({Constants.MESSAGE_RESULT: str(invalid_model_name)}),
            Constants.HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    module_path, class_name = data.get_module_and_class_from_a_model(
        parent_name)

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
        request_validator.valid_method_parameters_validator(
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

    module_path, class_name = data.get_module_and_class_from_a_executor_name(
        filename)

    class_method = data.get_class_method_from_a_executor_name(filename)
    try:
        request_validator.valid_method_parameters_validator(
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
