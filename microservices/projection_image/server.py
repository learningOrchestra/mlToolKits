from flask import jsonify, request, Flask
import os
from projection import Projection
from utils import Database, UserRequest, Metadata
from pyspark.sql import SparkSession

SPARKMASTER_HOST = "SPARKMASTER_HOST"
SPARKMASTER_PORT = "SPARKMASTER_PORT"
SPARK_DRIVER_PORT = "SPARK_DRIVER_PORT"
PROJECTION_HOST_NAME = "PROJECTION_HOST_NAME"

HTTP_STATUS_CODE_SUCCESS_CREATED = 201
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

MESSAGE_RESULT = "result"
PROJECTION_FILENAME_NAME = "outputDatasetName"
PARENT_FILENAME_NAME = "inputDatasetName"
FIELDS_NAME = "names"

MICROSERVICE_URI_GET = "/api/learningOrchestra/v1/transform/projection/"
MICROSERVICE_URI_GET_PARAMS = "?query={}&limit=20&skip=0"

FIRST_ARGUMENT = 0

app = Flask(__name__)

database_url = os.environ[DATABASE_URL]
database_replica_set = os.environ[DATABASE_REPLICA_SET]
database_name = os.environ[DATABASE_NAME]
database = Database(
    database_url,
    database_replica_set,
    os.environ[DATABASE_PORT],
    database_name,
)
request_validator = UserRequest(database)
metadata_creator = Metadata(database)

spark_session = SparkSession.builder. \
    appName("transform/projection"). \
    config("spark.driver.port", os.environ[SPARK_DRIVER_PORT]). \
    config("spark.driver.host", os.environ[PROJECTION_HOST_NAME]). \
    config("spark.jars.packages",
           "org.mongodb.spark:mongo-spark-connector_2.11:2.4.2",
           ). \
    config("spark.cores.max", 3). \
    config("spark.executor.cores", 3). \
    config("spark.executor.memory", "512m"). \
    config("spark.scheduler.mode", "FAIR"). \
    config("spark.scheduler.pool", "transform/projection"). \
    config("spark.scheduler.allocation.file",
           "./fairscheduler.xml"). \
    master(
    f'spark://{os.environ[SPARKMASTER_HOST]}:'
    f'{str(os.environ[SPARKMASTER_PORT])}'
). \
    getOrCreate()


@app.route("/projections", methods=["POST"])
def create_projection():
    parent_filename = request.json[PARENT_FILENAME_NAME]
    projection_filename = request.json[PROJECTION_FILENAME_NAME]
    projection_fields = request.json[FIELDS_NAME]

    request_errors = analyse_request_errors(
        request_validator,
        parent_filename,
        projection_filename,
        projection_fields)

    if request_errors is not None:
        return request_errors

    database_url_input = Database.collection_database_url(
        database_url,
        database_name,
        parent_filename,
        database_replica_set,
    )

    database_url_output = Database.collection_database_url(
        database_url,
        database_name,
        projection_filename,
        database_replica_set,
    )

    projection = Projection(metadata_creator, spark_session)
    projection.create(
        parent_filename, projection_filename,
        projection_fields, database_url_input, database_url_output)

    return (
        jsonify({
            MESSAGE_RESULT:
                f'{MICROSERVICE_URI_GET}{projection_filename}'
                f'{MICROSERVICE_URI_GET_PARAMS}'}),
        HTTP_STATUS_CODE_SUCCESS_CREATED,
    )


def analyse_request_errors(request_validator, parent_filename,
                           projection_filename, fields_name):
    try:
        request_validator.projection_filename_validator(
            projection_filename
        )
    except Exception as invalid_projection_filename:
        return (
            jsonify({MESSAGE_RESULT: invalid_projection_filename.args[
                FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_CONFLICT,
        )

    try:
        request_validator.filename_validator(parent_filename)
    except Exception as invalid_filename:
        return (
            jsonify({MESSAGE_RESULT: invalid_filename.args[FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    try:
        request_validator.projection_fields_validator(
            parent_filename, fields_name
        )
    except Exception as invalid_fields:
        return (
            jsonify({MESSAGE_RESULT: invalid_fields.args[FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    try:
        request_validator.finished_processing_validator(
            parent_filename)
    except Exception as unfinished_filename:
        return jsonify(
            {MESSAGE_RESULT: unfinished_filename.args[FIRST_ARGUMENT]}), \
               HTTP_STATUS_CODE_NOT_ACCEPTABLE

    return None


if __name__ == "__main__":
    app.run(
        host=os.environ[PROJECTION_HOST_IP],
        port=int(os.environ[PROJECTION_HOST_PORT])
    )
