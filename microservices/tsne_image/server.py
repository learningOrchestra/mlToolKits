from flask import jsonify, request, Flask, send_file
import os
from tsne import TsneGenerator, MongoOperations, TsneRequestValidator

HTTP_STATUS_CODE_SUCESS = 200
HTTP_STATUS_CODE_SUCESS_CREATED = 201
HTTP_STATUS_CODE_CONFLICT = 409
HTTP_STATUS_CODE_NOT_ACCEPTABLE = 406
HTTP_STATUS_CODE_NOT_FOUND = 404

TSNE_HOST_IP = "TSNE_HOST_IP"
TSNE_HOST_PORT = "TSNE_HOST_PORT"

IMAGES_PATH = "IMAGES_PATH"
IMAGE_FORMAT = ".png"

DATABASE_URL = "DATABASE_URL"
DATABASE_PORT = "DATABASE_PORT"
DATABASE_NAME = "DATABASE_NAME"
DATABASE_REPLICA_SET = "DATABASE_REPLICA_SET"
FULL_DATABASE_URL = (
        os.environ[DATABASE_URL] + "/?replicaSet=" + os.environ[
    DATABASE_REPLICA_SET]
)

GET = "GET"
POST = "POST"
DELETE = "DELETE"

MESSAGE_RESULT = "result"
TSNE_FILENAME_NAME = "output_filename"
LABEL_NAME = "label_name"

MESSAGE_CREATED_FILE = "created_file"
MESSAGE_DELETED_FILE = "deleted_file"
MESSAGE_NOT_FOUND = "not_found_file"

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


@app.route("/images", methods=[POST])
def create_tsne():
    database = MongoOperations(
        FULL_DATABASE_URL, os.environ[DATABASE_PORT], os.environ[DATABASE_NAME]
    )
    request_validator = TsneRequestValidator(database)

    try:
        request_validator.tsne_filename_existence_validator(
            request.json[TSNE_FILENAME_NAME]
        )
    except Exception as invalid_tsne_filename:
        return (
            jsonify(
                {MESSAGE_RESULT: invalid_tsne_filename.args[FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_CONFLICT,
        )

    try:
        parent_filename = request.json["input_filename"]
        request_validator.parent_filename_validator(parent_filename)
    except Exception as invalid_filename:
        return (
            jsonify({MESSAGE_RESULT: invalid_filename.args[FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    try:
        request_validator.filename_label_validator(
            parent_filename, request.json[LABEL_NAME]
        )
    except Exception as invalid_label:
        return (
            jsonify({MESSAGE_RESULT: invalid_label.args[FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_NOT_ACCEPTABLE,
        )

    database_url_input = collection_database_url(
        os.environ[DATABASE_URL],
        os.environ[DATABASE_NAME],
        parent_filename,
        os.environ[DATABASE_REPLICA_SET],
    )

    tsne_generator = TsneGenerator(database_url_input)

    tsne_generator.create_image(
        parent_filename, request.json[LABEL_NAME],
        request.json[TSNE_FILENAME_NAME]
    )

    return (
        jsonify({MESSAGE_RESULT: MESSAGE_CREATED_FILE}),
        HTTP_STATUS_CODE_SUCESS_CREATED,
    )


@app.route("/images", methods=[GET])
def get_images():
    images = os.listdir(os.environ[IMAGES_PATH])
    return jsonify({MESSAGE_RESULT: images}), HTTP_STATUS_CODE_SUCESS


@app.route("/images/<filename>", methods=[GET])
def get_image(filename):
    database = MongoOperations(
        FULL_DATABASE_URL, os.environ[DATABASE_PORT], os.environ[DATABASE_NAME]
    )
    request_validator = TsneRequestValidator(database)

    try:
        request_validator.no_tsne_filename_existence_validator(filename)
    except Exception as invalid_tsne_filename:
        return (
            jsonify(
                {MESSAGE_RESULT: invalid_tsne_filename.args[FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_NOT_FOUND,
        )

    image_path = os.environ[IMAGES_PATH] + "/" + filename + IMAGE_FORMAT

    return send_file(image_path, mimetype="image/png")


@app.route("/images/<filename>", methods=[DELETE])
def delete_image(filename):
    database = MongoOperations(
        FULL_DATABASE_URL, os.environ[DATABASE_PORT], os.environ[DATABASE_NAME]
    )
    request_validator = TsneRequestValidator(database)

    try:
        request_validator.no_tsne_filename_existence_validator(filename)
    except Exception as invalid_tsne_filename:
        return (
            jsonify(
                {MESSAGE_RESULT: invalid_tsne_filename.args[FIRST_ARGUMENT]}),
            HTTP_STATUS_CODE_NOT_FOUND,
        )

    image_path = os.environ[IMAGES_PATH] + "/" + filename + IMAGE_FORMAT
    os.remove(image_path)

    return jsonify(
        {MESSAGE_RESULT: MESSAGE_DELETED_FILE}), HTTP_STATUS_CODE_SUCESS


if __name__ == "__main__":
    app.run(host=os.environ[TSNE_HOST_IP],
            port=int(os.environ[TSNE_HOST_PORT]))
