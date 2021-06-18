class Constants:
    DEFAULT_MODEL_HOST_IP = ''
    DEFAULT_MODEL_HOST_PORT = ''

    DATABASE_URL = "DATABASE_URL"
    DATABASE_PORT = "DATABASE_PORT"
    DATABASE_NAME = "DATABASE_NAME"
    DATABASE_REPLICA_SET = "DATABASE_REPLICA_SET"

    MICROSERVICE_IP = "MICROSERVICE_IP"
    MICROSERVICE_PORT = "MICROSERVICE_PORT"

    MESSAGE_RESULT = "result"
    DELETED_MESSAGE = "deleted observer"

    HTTP_STATUS_CODE_SUCCESS_CREATED = 201
    HTTP_STATUS_CODE_SUCCESS_FULFILLED = 200
    HTTP_STATUS_CODE_BAD_REQUEST = 400
    HTTP_STATUS_CODE_CONFLICT = 409
    HTTP_STATUS_CODE_NOT_ACCEPTABLE = 406

    REQUEST_JSON_OBSERVE_TYPE = 'observe_type'
    REQUEST_JSON_TIMEOUT = 'timeout'
    REQUEST_OBSERVER_NAME = 'observer_name'
    REQUEST_JSON_FILENAME = 'filename'
    REQUEST_JSON_CUSTOM_PIPELINE = 'pipeline'

    MICROSERVICE_URI_PATH = "/api/learningOrchestra/v1/observer"

    MONGO_WAIT_PIPELINE = \
        {
            '$match': {
                '$and':
                    [
                        {'operationType': 'update'},
                        {'fullDocument.finished': {'$eq': True}}
                    ]
            }
        }
    MONGO_OBSERVE_PIPELINE = \
        {
            '$match': {
                '$or': [
                    {'operationType': 'update'},
                    {'operationType': 'insert'},
                    {'operationType': 'replace'},
                    {'operationType': 'delete'}
                ]
            }
        }
    MONGO_FIELDS_PIPELINE = \
        {
            '$addFields': {
                'clusterTime': {'$dateToString': {'date': '$clusterTime',
                                                  'format': '%d/%m/%G'}}
            }
        }

    DEFAULT_OBSERVER_NAME_PREFIX = 'observer_'

    OBSERVER_TYPE_WAIT = 'wait'
    OBSERVER_TYPE_OBSERVE = 'observe'
    OBSERVER_TYPE_CUSTOM = 'custom'