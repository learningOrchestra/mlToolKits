from flask import jsonify, request, Flask
import os
from model_builder import SparkModelBuilder
import pickle

HTTP_STATUS_CODE_SUCESS_CREATED = 201

MODEL_BUILDER_HOST_IP = "MODEL_BUILDER_HOST_IP"
MODEL_BUILDER_HOST_PORT = "MODEL_BUILDER_HOST_PORT"

GET = 'GET'
POST = 'POST'
DELETE = 'DELETE'

MESSAGE_RESULT = "result"
MESSAGE_CREATED_FILE = "created_file"

ENCODED_ASSEMBLER = "encoded_assembler"
MODEL_CLASSIFICATOR = "model_classificator"
DATABASE_URL_TRAINING = "database_url_training"
DATABASE_URL_TESTING = "database_url_testing"

app = Flask(__name__)


@app.route('/models', methods=[POST])
def create_model():
    model_builder = SparkModelBuilder()
    data = pickle.loads(request.get_data())
    model_builder.build_model(
        data[DATABASE_URL_TRAINING],
        data[DATABASE_URL_TESTING],
        data[ENCODED_ASSEMBLER],
        data[MODEL_CLASSIFICATOR]
    )

    return jsonify({MESSAGE_RESULT: MESSAGE_CREATED_FILE}), \
        HTTP_STATUS_CODE_SUCESS_CREATED


if __name__ == "__main__":
    app.run(host=os.environ[MODEL_BUILDER_HOST_IP],
            port=int(os.environ[MODEL_BUILDER_HOST_PORT]), debug=True)
