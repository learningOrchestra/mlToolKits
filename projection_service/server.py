from flask import jsonify, request, Flask
import os
from flask_cors import CORS
from pyspark.sql import SparkSession
from projection import SparkManager

HTTP_STATUS_CODE_SUCESS_CREATED = 201

PROJECTION_HOST = "PROJECTION_HOST"
PROJECTION_PORT = "PROJECTION_PORT"

DATABASE_URL = "DATABASE_URL"
DATABASE_NAME = "DATABASE_NAME"
DATABASE_REPLICA_SET = "DATABASE_REPLICA_SET"
DOCUMENT_ID = '_id'

GET = 'GET'
POST = 'POST'
DELETE = 'DELETE'

MESSAGE_RESULT = "result"

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
    database_url_input = collection_database_url(
                            os.environ[DATABASE_URL],
                            os.environ[DATABASE_NAME],
                            request.json["filename"],
                            os.environ[DATABASE_REPLICA_SET])

    database_url_output = collection_database_url(
                            os.environ[DATABASE_URL],
                            os.environ[DATABASE_NAME],
                            request.json["projection_filename"],
                            os.environ[DATABASE_REPLICA_SET])

    spark_manager = SparkManager(
                            database_url_input,
                            database_url_output)

    projection_fields = request.json['fields']
    if(DOCUMENT_ID not in projection_fields):
        projection_fields.append(DOCUMENT_ID)

    spark_manager.projection(projection_fields)

    return jsonify(
        {MESSAGE_RESULT: SparkManager.MESSAGE_CREATED_FILE}),\
        HTTP_STATUS_CODE_SUCESS_CREATED


if __name__ == "__main__":
    app.run(host=os.environ[PROJECTION_HOST],
            port=int(os.environ[PROJECTION_PORT]))
