from flask import jsonify, request, Flask
import os
from flask_cors import CORS
from pyspark.sql import SparkSession
from projection import SparkManager

HTTP_STATUS_CODE_SUCESS_CREATED = 201

PROJECTION_HOST = "PROJECTION_HOST"
PROJECTION_PORT = "PROJECTION_PORT"

DATABASE_URL = "DATABASE_URL"
DATABASE_NAME = "db"

GET = 'GET'
POST = 'POST'
DELETE = 'DELETE'

MESSAGE_RESULT = "result"

app = Flask(__name__)
CORS(app)


@app.route('/projections', methods=[POST])
def create_projection():
    spark_manager = SparkManager(
                            os.environ[DATABASE_URL],
                            DATABASE_NAME,
                            request.json["filename"],
                            request.json[
                                "projection_filename"]
                                )
    spark_manager.projection(request.json['fields'])
    return jsonify(
        {MESSAGE_RESULT: SparkManager.MESSAGE_CREATED_FILE}),\
        HTTP_STATUS_CODE_SUCESS_CREATED


if __name__ == "__main__":
    app.run(host=os.environ[PROJECTION_HOST],
            port=int(os.environ[PROJECTION_PORT]), debug=True)
