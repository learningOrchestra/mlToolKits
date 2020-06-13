from flask import jsonify, request, Flask
import os
from flask_cors import CORS
from pyspark.sql import SparkSession
from projection import SparkManager, ProcessorInterface, MongoOperations
from bson.objectid import ObjectId

HTTP_STATUS_CODE_SUCESS_CREATED = 201
HTTP_STATUS_CODE_CONFLICT = 409
HTTP_STATUS_CODE_NOT_ACCEPTABLE = 406

PROJECTION_HOST_IP = "PROJECTION_HOST_IP"
PROJECTION_HOST_PORT = "PROJECTION_HOST_PORT"

DATABASE_URL = "DATABASE_URL"
DATABASE_NAME = "DATABASE_NAME"
DATABASE_REPLICA_SET = "DATABASE_REPLICA_SET"

DOCUMENT_ID = '_id'
METADATA_DOCUMENT_ID = 0

GET = 'GET'
POST = 'POST'
DELETE = 'DELETE'

MESSAGE_RESULT = "result"
FILENAME_NAME = "filename"
PROJECTION_FILENAME_NAME = "projection_filename"
FIELDS_NAME = "fields"

MESSAGE_MISSING_FIELDS = "missing_request_fields"
MESSAGE_INVALID_FIELDS = "invalid_fields"

app = Flask(__name__)
CORS(app)


def collection_database_url(database_url, database_name, database_filename,
                            database_replica_set):
    return database_url + '/' + \
        database_name + '.' + \
        database_filename + "?replicaSet=" + \
        database_replica_set + \
        "&authSource=admin"


@app.route('/projections', methods=[POST])
def create_projection():
    if(not (request.json[FILENAME_NAME] and
       request.json[PROJECTION_FILENAME_NAME] and
       request.json[FIELDS_NAME])):
        return jsonify(
            {MESSAGE_RESULT: MESSAGE_MISSING_FIELDS}),\
            HTTP_STATUS_CODE_NOT_ACCEPTABLE

    database = MongoOperations(
        os.environ[DATABASE_URL] + '/?replicaSet=' +
        os.environ[DATABASE_REPLICA_SET], os.environ[DATABASE_NAME])

    filename_metadata_query = {DOCUMENT_ID: ObjectId(METADATA_DOCUMENT_ID)}

    filename_metadata = database.find_one_in_file(
        request.json[FILENAME_NAME], filename_metadata_query)

    for field in request.json[FIELDS_NAME]:
        if field not in filename_metadata[FIELDS_NAME]:
            return jsonify(
                {MESSAGE_RESULT: MESSAGE_INVALID_FIELDS}),\
                HTTP_STATUS_CODE_NOT_ACCEPTABLE

    database_url_input = collection_database_url(
                            os.environ[DATABASE_URL],
                            os.environ[DATABASE_NAME],
                            request.json[FILENAME_NAME],
                            os.environ[DATABASE_REPLICA_SET])

    database_url_output = collection_database_url(
                            os.environ[DATABASE_URL],
                            os.environ[DATABASE_NAME],
                            request.json[PROJECTION_FILENAME_NAME],
                            os.environ[DATABASE_REPLICA_SET])

    spark_manager = SparkManager(
                            database_url_input,
                            database_url_output)

    projection_fields = request.json[FIELDS_NAME]

    if(DOCUMENT_ID not in projection_fields):
        projection_fields.append(DOCUMENT_ID)

    result = spark_manager.projection(
                request.json[FILENAME_NAME],
                request.json[PROJECTION_FILENAME_NAME],
                projection_fields)

    if(result == ProcessorInterface.MESSAGE_CREATED_FILE):
        return jsonify(
            {MESSAGE_RESULT: ProcessorInterface.MESSAGE_CREATED_FILE}),\
            HTTP_STATUS_CODE_SUCESS_CREATED

    elif(result == ProcessorInterface.MESSAGE_DUPLICATE_FILE):
        return jsonify(
            {MESSAGE_RESULT: ProcessorInterface.MESSAGE_DUPLICATE_FILE}),\
            HTTP_STATUS_CODE_CONFLICT


if __name__ == "__main__":
    app.run(host=os.environ[PROJECTION_HOST_IP],
            port=int(os.environ[PROJECTION_HOST_PORT]))
