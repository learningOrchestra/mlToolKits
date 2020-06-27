from flask import jsonify, request, Flask
import os
from flask_cors import CORS
from model_builder import SparkModelBuilder

HTTP_STATUS_CODE_SUCESS_CREATED = 201
HTTP_STATUS_CODE_CONFLICT = 409
HTTP_STATUS_CODE_NOT_ACCEPTABLE = 406

MODEL_BUILDER_HOST_IP = "MODEL_BUILDER_HOST_IP"
MODEL_BUILDER_HOST_PORT = "MODEL_BUILDER_HOST_PORT"

GET = 'GET'
POST = 'POST'
DELETE = 'DELETE'

MESSAGE_RESULT = "result"
MESSAGE_CREATED_FILE = "created_file"

app = Flask(__name__)
CORS(app)


@app.route('/models', methods=[POST])
def create_model():
    model_constructor = SparkModelBuilder()
    model_constructor.build_model()

    return jsonify({MESSAGE_RESULT: MESSAGE_CREATED_FILE}), \
        HTTP_STATUS_CODE_SUCESS_CREATED


if __name__ == "__main__":
    app.run(host=os.environ[MODEL_BUILDER_HOST_IP],
            port=int(os.environ[MODEL_BUILDER_HOST_PORT]), debug=True)
