from flask import jsonify, request, Flask
import os
from binary_execution import Execution
from utils import *
from typing import Union
from constants import *

app = Flask(__name__)

DATABASE_URL = os.environ[DATABASE_URL]
DATABASE_REPLICA_SET = os.environ[DATABASE_REPLICA_SET]
DATABASE_NAME = os.environ[DATABASE_NAME]


@app.route("/binaryExecutor", methods=["POST"])
def create_execution() -> jsonify:
    service_type = request.args.get(TYPE_FIELD_NAME)

    parent_name = request.json[PARENT_NAME_FIELD_NAME]
    filename = request.json[NAME_FIELD_NAME]
    description = request.json[DESCRIPTION_FIELD_NAME]
    class_method = request.json[METHOD_FIELD_NAME]
    method_parameters = request.json[METHOD_PARAMETERS_FIELD_NAME]

    database = Database(
        DATABASE_URL,
        DATABASE_REPLICA_SET,
        int(os.environ[DATABASE_PORT]),
        DATABASE_NAME,
    )

    request_validator = UserRequest(database)

    request_errors = analyse_post_request_errors(
        request_validator,
        database,
        filename,
        parent_name,
        class_method,
        method_parameters)

    if request_errors is not None:
        return request_errors

    metadata_creator = Metadata(database)
    train_model = Execution(
        database,
        filename,
        service_type,
        parent_name,
        metadata_creator,
        class_method
    )

    data = Data(database)
    module_path, class_name = data.get_module_and_class_from_a_model(
        parent_name)
    train_model.execute(
        module_path, method_parameters, description)

    return (
        jsonify({
            MESSAGE_RESULT:
                MICROSERVICE_URI_SWITCHER[service_type] +
                filename +
                MICROSERVICE_URI_GET_PARAMS}),
        HTTP_STATUS_CODE_SUCCESS_CREATED,
    )


@app.route("/binaryExecutor/<filename>", methods=["PATCH"])
def update_execution(filename: str) -> jsonify:
    service_type = request.args.get(TYPE_FIELD_NAME)

    database = Database(
        DATABASE_URL,
        DATABASE_REPLICA_SET,
        int(os.environ[DATABASE_PORT]),
        DATABASE_NAME,
    )

    description = request.json[DESCRIPTION_FIELD_NAME]
    method_parameters = request.json[METHOD_PARAMETERS_FIELD_NAME]

    request_validator = UserRequest(database)

    request_errors = analyse_patch_request_errors(
        request_validator,
        database,
        filename,
        method_parameters)

    if request_errors is not None:
        return request_errors

    data = Data(database)
    module_path, function = data.get_module_and_class_from_a_model(
        filename)
    model_name = data.get_model_name_from_a_child(filename)
    method_name = data.get_class_method_from_a_executor_name(filename)

    metadata_creator = Metadata(database)
    default_model = Execution(database, filename, service_type, model_name,
                              metadata_creator,
                              method_name)

    default_model.update(
        module_path, method_parameters, description)

    return (
        jsonify({
            MESSAGE_RESULT:
                MICROSERVICE_URI_SWITCHER[service_type] +
                filename +
                MICROSERVICE_URI_GET_PARAMS}),
        HTTP_STATUS_CODE_SUCCESS_CREATED,
    )


@app.route("/defaultModel/<filename>", methods=["DELETE"])
def delete_default_model(filename: str) -> jsonify:
    database_url = os.environ[DATABASE_URL]
    database_replica_set = os.environ[DATABASE_REPLICA_SET]
    database_name = os.environ[DATABASE_NAME]
    service_type = request.args.get("type")

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

    default_model = Execution(database, filename, service_type)
    default_model.delete()


def analyse_post_request_errors(request_validator: UserRequest,
                                database: Database,
                                train_name: str,
                                model_name: str,
                                class_method: str,
                                method_parameters: dict) \
        -> Union[tuple, None]:
    try:
        request_validator.not_duplicated_filename_validator(
            train_name
        )
    except Exception as duplicated_train_filename:
        return (
            jsonify({MESSAGE_RESULT: str(duplicated_train_filename)}),
            HTTP_STATUS_CODE_CONFLICT,
        )

    try:
        request_validator.existent_filename_validator(
            model_name
        )
    except Exception as invalid_model_name:
        return (
            jsonify({MESSAGE_RESULT: str(invalid_model_name)}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    data = Data(database)
    module_path, class_name = data.get_module_and_class_from_a_model(
        model_name)

    try:
        request_validator.valid_method_class_validator(
            module_path,
            class_name,
            class_method
        )
    except Exception as invalid_method_name:
        return (
            jsonify({MESSAGE_RESULT: str(invalid_method_name)}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
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
            jsonify({MESSAGE_RESULT: str(invalid_method_parameters)}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    return None


def analyse_patch_request_errors(request_validator: UserRequest,
                                 database: Database,
                                 train_name: str,
                                 method_parameters: dict) \
        -> Union[tuple, None]:
    try:
        request_validator.existent_filename_validator(
            train_name
        )
    except Exception as nonexistent_train_filename:
        return (
            jsonify({MESSAGE_RESULT: str(nonexistent_train_filename)}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    data = Data(database)
    module_path, class_name = data.get_module_and_class_from_a_executor_name(
        train_name)

    class_method = data.get_class_method_from_a_executor_name(train_name)
    try:
        request_validator.valid_method_parameters_validator(
            module_path,
            class_name,
            class_method,
            method_parameters
        )
    except Exception as invalid_function_parameters:
        return (
            jsonify({MESSAGE_RESULT: str(invalid_function_parameters)}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    return None


if __name__ == "__main__":
    app.run(
        host=os.environ["MICROSERVICE_IP"],
        port=int(os.environ["MICROSERVICE_PORT"])
    )