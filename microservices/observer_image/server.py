from typing import Optional

from flask import jsonify, Flask, request
import os
from pymongo import errors
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


@app.route("/observer/<filename>", methods=["POST"])
def create_collection_watcher(filename: str) -> jsonify:
    pipeline = [
        {
            '$match': {
                '$or': [{'operationType': 'update'},
                        {'operationType': 'insert'}]
            }
        },
        {
            '$addFields': {
                'clusterTime': {'$dateToString': {'date': '$clusterTime'}},
                'fullDocument._id': {'$toString': '$fullDocument._id'},
                'documentKey._id': {'$toString': '$documentKey._id'}
            }
        },
    ]

    try:
        cursor_name = db.watch(collection_name=filename, pipeline=pipeline)

        return successful_response(result={
            cursor_name: cursor_name
        })
    except errors.InvalidName:
        return error_response(Constants.MESSAGE_RESPONSE_DATABASE)


@app.route("/observer/<filename>", methods=["GET"])
def get_collection_data(filename: str) -> jsonify:
    args = request.args
    observer_index = try_get_args(args,[
        'index',
        'observer_index',
        'observer'
    ])

    if observer_index is None:
        observer_index = '0'

    observer_index = int(observer_index)

    try:
        cursor = db.get_cursor(collection_name=filename,
                               observer_index=observer_index)
    except KeyError:
        return error_response(Constants.MESSAGE_RESPONSE_DATABASE)
    except IndexError:
        return error_response(Constants.MESSAGE_RESPONSE_OBSERVER +
                              observer_index)

    change = cursor.next()
    return successful_response(result=change)


@app.route("/observer/<filename>", methods=["DELETE"])
def delete_collection_watcher(filename: str) -> jsonify:
    args = request.args
    observer_index = try_get_args(args, [
        'index',
        'observer_index',
        'observer'
    ])

    if observer_index is None:
        observer_index = '0'

    observer_index = int(observer_index)

    try:
        cursor = db.get_cursor(collection_name=filename,
                               observer_index=observer_index)
    except KeyError:
        return error_response(Constants.MESSAGE_RESPONSE_DATABASE)
    except IndexError:
        return error_response(Constants.MESSAGE_RESPONSE_OBSERVER +
                              observer_index)

    cursor.close()
    return successful_response(
        {
            Constants.MESSAGE_RESULT: Constants.DELETED_MESSAGE
        }
    )


def error_response(subject: str = '') -> jsonify:
    return (
        jsonify(
            {
                Constants.MESSAGE_RESULT: str(
                    subject + Constants.MESSAGE_RESPONSE_NOT_FOUND
                )
            }
        ),
        Constants.HTTP_STATUS_CODE_BAD_REQUEST
    )


def successful_response(result: dict) -> jsonify:

    return (
        jsonify(
            {
                Constants.MESSAGE_RESULT: result
            }
        ),
        Constants.HTTP_STATUS_CODE_SUCCESS_FULFIlLED
    )

def try_get_args(args: dict, args_list: []) -> Optional[str]:
    for arg in args_list:
        observer_index = args.get(arg)
        if(observer_index is not None):
            return observer_index

    return None

if __name__ == '__main__':
    app.run(
        host = os.environ[Constants.MICROSERVICE_IP],
        port = int(os.environ[Constants.MICROSERVICE_PORT])
    )
