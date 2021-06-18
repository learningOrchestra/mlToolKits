from typing import Optional, Union

from flask import jsonify, Flask, request
import os
from utils.constants import Constants
from utils.database import Database

database_url = os.environ[Constants.DATABASE_URL]
database_replica_set = os.environ[Constants.DATABASE_REPLICA_SET]
database_port = os.environ[Constants.DATABASE_PORT]
database_name = os.environ[Constants.DATABASE_NAME]

db = Database(
    database_url = database_url,
    database_name = database_name,
    database_port = int(database_port),
    replica_set = database_replica_set
)

app = Flask(__name__)

@app.route(f'{Constants.MICROSERVICE_URI_PATH}', methods=["POST"])
def create_collection_watcher() -> jsonify:
    filename = request.json[Constants.REQUEST_JSON_FILENAME]
    observer_type = request.json[Constants.REQUEST_JSON_OBSERVE_TYPE]

    try:
        timeout = request.json[Constants.REQUEST_JSON_TIMEOUT]
    except:
        timeout = 0
    try:
        observer_name = request.json[Constants.REQUEST_OBSERVER_NAME]
    except:
        observer_name = ''
    try:
        pipeline = request.json[Constants.REQUEST_JSON_CUSTOM_PIPELINE]
    except:
        pipeline = []
    try:
        timeout = int(timeout)
    except:
        return error_response('invalid timeout attribute value')

    try:
        cursor_name = db.submit(collection_name=filename,
                                observer_type=observer_type,
                                timeout=timeout,
                                observer_name=observer_name,
                                pipeline=pipeline)


        return successful_response(f'{Constants.MICROSERVICE_URI_PATH}/'
                                   f'{cursor_name}')
    except Exception as e:
        return error_response(str(e))


@app.route(f'{Constants.MICROSERVICE_URI_PATH}/<filename>/<observer_name>',
           methods=["GET"])
def get_collection_data(filename: str, observer_name: str) -> jsonify:
    try:
        change = db.watch(collection_name=filename,
                          observer_name=observer_name)
    except Exception as e:
        return error_response(str(e))

    return successful_response(result=change)


@app.route(f'{Constants.MICROSERVICE_URI_PATH}/<filename>/<observer_name>',
           methods=["DELETE"])
def delete_collection_watcher(filename: str, observer_name: str) -> jsonify:
    try:
        db.remove_watch(collection_name=filename,
                        observer_name=observer_name)
    except Exception as e:
        return error_response(str(e))

    return successful_response(Constants.DELETED_MESSAGE)


def error_response(subject: str = '') -> jsonify:
    return (
        jsonify(
            {
                Constants.MESSAGE_RESULT: str(subject)
            }
        ),
        Constants.HTTP_STATUS_CODE_BAD_REQUEST
    )


def successful_response(result: Union[dict, str]) -> jsonify:

    return (
        jsonify(
            {
                Constants.MESSAGE_RESULT: result
            }
        ),
        Constants.HTTP_STATUS_CODE_SUCCESS_FULFILLED
    )

if __name__ == '__main__':
    app.run(
        host = os.environ[Constants.MICROSERVICE_IP],
        port = int(os.environ[Constants.MICROSERVICE_PORT])
    )
