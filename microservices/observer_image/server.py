import traceback
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
    try:
        filename = request.json[Constants.REQUEST_JSON_FILENAME]
    except:
        return error_response('missing filename value')
    try:
        observer_type = request.json[Constants.REQUEST_JSON_OBSERVE_TYPE]
    except:
        return error_response('missing observer_type value')
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
        return error_response('invalid timeout value')

    try:
        cursor_name = db.submit(collection_name=filename,
                                observer_type=observer_type,
                                timeout=timeout,
                                observer_name=observer_name,
                                pipeline=pipeline)


        return successful_response(f'{Constants.MICROSERVICE_URI_PATH}/'
                                   f'{cursor_name}')
    except KeyError as ke:
        return error_response(str(ke),Constants.HTTP_STATUS_CODE_NOT_ACCEPTABLE)
    except Exception as e:
        return error_response(str(e))


@app.route(f'{Constants.MICROSERVICE_URI_PATH}/<filename>/<observer_name>',
           methods=["GET"])
def get_collection_data(filename: str, observer_name: str) -> jsonify:
    try:
        change = db.watch(collection_name=filename,
                      observer_name=observer_name)
    except ValueError as ve:
        return error_response(str(ve),Constants.HTTP_STATUS_CODE_NOT_ACCEPTABLE)
    except Exception as e:
        return error_response(str(e))

    if change is None:
        return error_response('observer timed out',
                              code=Constants.HTTP_STATUS_CODE_TIMED_OUT)

    return successful_response(result=change)


@app.route(f'{Constants.MICROSERVICE_URI_PATH}/<filename>/<observer_name>',
           methods=["PATCH"])
def update_collection_watcher(filename: str, observer_name: str) -> jsonify:
    try:
        observer_type = request.json[Constants.REQUEST_JSON_OBSERVE_TYPE]
    except:
        observer_type = None
    try:
        timeout = request.json[Constants.REQUEST_JSON_TIMEOUT]
    except:
        timeout = None
    try:
        pipeline = request.json[Constants.REQUEST_JSON_CUSTOM_PIPELINE]
    except:
        pipeline = None
    try:
        new_observer = request.json[Constants.REQUEST_JSON_NEW_OBSERVER_NAME]
    except:
        new_observer = None
    try:
        new_collection = \
            request.json[Constants.REQUEST_JSON_NEW_COLLECTION_NAME]
    except:
        new_collection = None
    try:
        if timeout is not None:
            timeout = int(timeout)
    except:
        return error_response('invalid timeout value')
    try:
        cursor_name = db.update_watch(filename,observer_name,new_collection,
                                      new_observer, observer_type,timeout,
                                      pipeline)
    except ValueError as ve:
        return error_response(str(ve),Constants.HTTP_STATUS_CODE_NOT_ACCEPTABLE)
    except Exception as e:
        return error_response(str(e))

    return successful_response(f'{Constants.MICROSERVICE_URI_PATH}/'
                               f'{cursor_name}')


@app.route(f'{Constants.MICROSERVICE_URI_PATH}/<filename>/<observer_name>',
           methods=["DELETE"])
def delete_collection_watcher(filename: str, observer_name: str) -> jsonify:
    try:
        db.remove_watch(collection_name=filename,
                        observer_name=observer_name)
    except ValueError as ve:
        return error_response(str(ve),Constants.HTTP_STATUS_CODE_NOT_ACCEPTABLE)
    except Exception as e:
        return error_response(str(e))

    return successful_response(Constants.DELETED_MESSAGE)


def error_response(subject: str = '',
                   code: int=Constants.HTTP_STATUS_CODE_BAD_REQUEST) -> jsonify:
    return (
        jsonify(
            {
                Constants.MESSAGE_RESULT: str(subject)
            }
        ),
        code
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
