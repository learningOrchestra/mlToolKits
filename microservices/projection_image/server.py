from flask import jsonify, request, Flask
import os
from projection import SparkManager, MongoOperations, \
    ProjectionRequestValidator
from concurrent.futures import ThreadPoolExecutor

HTTP_STATUS_CODE_SUCESS_CREATED = 201
HTTP_STATUS_CODE_CONFLICT = 409
HTTP_STATUS_CODE_NOT_ACCEPTABLE = 406

PROJECTION_HOST_IP = "PROJECTION_HOST_IP"
PROJECTION_HOST_PORT = "PROJECTION_HOST_PORT"

DATABASE_URL = "DATABASE_URL"
DATABASE_PORT = "DATABASE_PORT"
DATABASE_NAME = "DATABASE_NAME"
DATABASE_REPLICA_SET = "DATABASE_REPLICA_SET"

DOCUMENT_ID = "_id"
METADATA_DOCUMENT_ID = 0

GET = "GET"
POST = "POST"
DELETE = "DELETE"

MESSAGE_RESULT = "result"
PROJECTION_FILENAME_NAME = "output_filename"
FIELDS_NAME = "names"

FIRST_ARGUMENT = 0

app = Flask(__name__)


def collection_database_url(
        database_url, database_name, database_filename, database_replica_set
):
    return (
            database_url
            + "/"
            + database_name
            + "."
            + database_filename
            + "?replicaSet="
            + database_replica_set
            + "&authSource=admin"
    )


thread_pool = ThreadPoolExecutor()


@app.route("/projections", methods=[POST])
def create_projection():
    database = MongoOperations(
        os.environ[DATABASE_URL] + "/?replicaSet=" + os.environ[
            DATABASE_REPLICA_SET],
        os.environ[DATABASE_PORT],
        os.environ[DATABASE_NAME],
    )

    request_validator = ProjectionRequestValidator(database)

    try:
        request_validator.projection_filename_validator(
            request.json[PROJECTION_FILENAME_NAME]
        )
    except Exception as invalid_projection_filename:
        return (
            jsonify({MESSAGE_RESULT: invalid_projection_filename.args[
                FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_CONFLICT,
        )

    try:
        parent_filename = request.json["input_filename"]
        request_validator.filename_validator(parent_filename)
    except Exception as invalid_filename:
        return (
            jsonify({MESSAGE_RESULT: invalid_filename.args[FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    try:
        request_validator.projection_fields_validator(
            parent_filename, request.json[FIELDS_NAME]
        )
    except Exception as invalid_fields:
        return (
            jsonify({MESSAGE_RESULT: invalid_fields.args[FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    database_url_input = collection_database_url(
        os.environ[DATABASE_URL],
        os.environ[DATABASE_NAME],
        parent_filename,
        os.environ[DATABASE_REPLICA_SET],
    )

    database_url_output = collection_database_url(
        os.environ[DATABASE_URL],
        os.environ[DATABASE_NAME],
        request.json[PROJECTION_FILENAME_NAME],
        os.environ[DATABASE_REPLICA_SET],
    )

    spark_manager = SparkManager(database_url_input, database_url_output)

    projection_fields = request.json[FIELDS_NAME]

    thread_pool.submit(spark_manager.projection,
                       parent_filename, request.json[PROJECTION_FILENAME_NAME],
                       projection_fields)

    return (
        jsonify({
            MESSAGE_RESULT:
                "/api/learningOrchestra/v1/transform/projection/" +
                request.json["output_filename"] +
                "?query={}&limit=10&skip=0"}),
        HTTP_STATUS_CODE_SUCESS_CREATED,
    )


if __name__ == "__main__":
    app.run(
        host=os.environ[PROJECTION_HOST_IP],
        port=int(os.environ[PROJECTION_HOST_PORT])
    )
