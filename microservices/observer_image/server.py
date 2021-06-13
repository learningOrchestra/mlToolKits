from typing import Optional, Union

from flask import jsonify, Flask, request
import os
from pymongo import errors
from utils.constants import Constants
from utils.database import Database
from utils.utils import Utils

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
    observe_type = request.json[Constants.REQUEST_JSON_OBSERVE_TYPE]
    timeout = request.json[Constants.REQUEST_JSON_TIMEOUT]

    print("OBSERVE TYPE = " + observe_type, flush=True)
    if observe_type == '' or observe_type == '1' or observe_type == 'wait':
        observe_pipeline = {
            '$match': {
                '$and':
                    [
                        {'operationType': 'update'},
                        {'fullDocument.finished': {'$eq': True}}
                    ]
            }
        }
    elif observe_type == '2' or observe_type == 'observe':
        observe_pipeline = {
            '$match': {
                '$or': [
                    {'operationType': 'update'},
                    {'operationType': 'insert'},
                    {'operationType': 'replace'},
                    {'operationType': 'delete'}
                ]
            }
        }
    else:
        return error_response(f'{Constants.MESSAGE_RESPONSE_QUERY} '
                              f'observe_type={observe_type}')

    pipeline = [
        observe_pipeline,
        {
            '$addFields': {
                'clusterTime': {'$dateToString': {'date': '$clusterTime',
                                                  'format': '%d/%m/%G'}}
            }
        },
    ]

    print('a1',flush=True)
    if timeout == '' or timeout is None:
        timeout = 0
    else:
        try:
            timeout = int(timeout)
        except:
            return error_response(f'{Constants.MESSAGE_RESPONSE_QUERY} '
                                  f'timeout={timeout}')


    print('a2',flush=True)
    try:
        cursor_name = db.submit(collection_name=filename,
                               pipeline=pipeline,
                               timeout=timeout)

        return successful_response(f'{Constants.API_PATH}'
                                   f'{Constants.MICROSERVICE_URI_PATH}/'
                                   f'{cursor_name}')
    except:
        return error_response(f'{Constants.MESSAGE_RESPONSE_FILENAME} '
                              f'{filename}')


@app.route(f'{Constants.MICROSERVICE_URI_PATH}/<filename>', methods=["GET"])
def get_collection_data(filename: str) -> jsonify:
    args = request.args
    observer_index = Utils.try_get_args(args,[
        'index',
        'observer_index',
        'observer'
    ])

    print("URL: " + request.url,flush=True)
    print(args.keys(),flush=True)
    print(args.values(),flush=True)
    if observer_index is None:
        observer_index = '0'

    observer_index = int(observer_index)

    try:
        change = db.watch(collection_name=filename,
                          observer_index=observer_index)
    except KeyError:
        print(f'ERROR {Constants.MESSAGE_RESPONSE_FILENAME}',flush=True)
        return error_response(f'{Constants.MESSAGE_RESPONSE_FILENAME} '
                              f'{filename}')
    except IndexError:
        print(f'ERROR {Constants.MESSAGE_RESPONSE_OBSERVER}', flush=True)
        return error_response(f'{Constants.MESSAGE_RESPONSE_OBSERVER} '
                              f'{observer_index}')

    print(change, flush=True)
    return successful_response(result=change)


@app.route(f'{Constants.MICROSERVICE_URI_PATH}/<filename>', methods=["DELETE"])
def delete_collection_watcher(filename: str) -> jsonify:
    args = request.args
    observer_index = Utils.try_get_args(args, [
        'index',
        'observer_index',
        'observer'
    ])

    if observer_index is None:
        observer_index = '0'

    observer_index = int(observer_index)

    try:
        cursor = db.remove_watch(collection_name=filename,
                                 observer_index=observer_index)
    except KeyError:
        return error_response(f'{Constants.MESSAGE_RESPONSE_FILENAME} '
                              f'{filename}')
    except IndexError:
        return error_response(f'{Constants.MESSAGE_RESPONSE_OBSERVER} '
                              f'{observer_index}')

    cursor.close()
    return successful_response(Constants.DELETED_MESSAGE)


def error_response(subject: str = '') -> jsonify:
    return (
        jsonify(
            {
                Constants.MESSAGE_RESULT: str(
                    f'{Constants.MESSAGE_RESPONSE_INVALID} {subject}'
                )
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
        Constants.HTTP_STATUS_CODE_SUCCESS_FULFIlLED
    )

if __name__ == '__main__':
    app.run(
        host = os.environ[Constants.MICROSERVICE_IP],
        port = int(os.environ[Constants.MICROSERVICE_PORT])
    )
