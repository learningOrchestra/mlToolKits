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

GET = 'GET'
POST = 'POST'
DELETE = 'DELETE'

MESSAGE_RESULT = "result"

app = Flask(__name__)
CORS(app)


@app.route('/projections', methods=[POST])
def create_projection():
    database_url_input = os.envirion(DATABASE_URL) + '/' + \
        os.environ(DATABASE_NAME) + '.' + \
        request.json["filename"] + "?replicaSet=" + \
        os.environ(DATABASE_REPLICA_SET)

    database_url_output = os.envirion(DATABASE_URL) + '/' + \
        os.environ(DATABASE_NAME) + '.' + \
        request.json["projection_filename"] + "?replicaSet=" + \
        os.environ(DATABASE_REPLICA_SET)

    spark_manager = SparkManager(
                            database_url_input,
                            database_url_output)

    spark_manager.projection(request.json['fields'])
    return jsonify(
        {MESSAGE_RESULT: SparkManager.MESSAGE_CREATED_FILE}),\
        HTTP_STATUS_CODE_SUCESS_CREATED


if __name__ == "__main__":
    app.run(host=os.environ[PROJECTION_HOST],
            port=int(os.environ[PROJECTION_PORT]))
