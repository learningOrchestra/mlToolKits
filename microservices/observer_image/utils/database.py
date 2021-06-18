from typing import Union

from pymongo import MongoClient, errors
from pymongo.change_stream import CollectionChangeStream
from utils.constants import Constants


class Database:
    __TIMEOUT_TIME_MULTIPLICATION = 1000

    def __init__(self, database_url: str, replica_set: str, database_port: int,
                 database_name: str):

        self.mongo_client = MongoClient(
            f'{database_url}', int(database_port),
            replicaSet=replica_set
        )

        self.database = self.mongo_client[database_name]
        self.cursors_array = dict()

    def submit(self, collection_name: str,
               observer_type:str= Constants.OBSERVER_TYPE_WAIT,
               timeout: int=0, observer_name:str='', pipeline:[]=None) -> str:

        if pipeline is None:
            pipeline = []

        print('p1.1', flush=True)
        if collection_name not in self.database.list_collection_names():
            raise KeyError('collection not found')

        print('p1.2', flush=True)
        if observer_type == '' or observer_type == Constants.OBSERVER_TYPE_WAIT:
            pipeline = [Constants.MONGO_WAIT_PIPELINE,
                        Constants.MONGO_FIELDS_PIPELINE]
        elif observer_type == Constants.OBSERVER_TYPE_OBSERVE:
            pipeline = [Constants.MONGO_OBSERVE_PIPELINE,
                        Constants.MONGO_FIELDS_PIPELINE]
        elif observer_type != Constants.OBSERVER_TYPE_CUSTOM:
            raise ValueError(f'invalid observer_type value: {observer_type}')

        collection = self.database[collection_name]
        cursor = collection.watch(
            pipeline=pipeline,
            full_document='updateLookup',
            max_await_time_ms=timeout
        )

        print('p1.3', flush=True)
        if observer_name == '':
            observer_name = self.__get_default_observer_name(collection_name)
        elif collection_name in self.cursors_array.keys():
            if observer_name in self.cursors_array[collection_name].keys():
                return f'{collection_name}/{observer_name}'

        print('p1.4', flush=True)
        if collection_name in self.cursors_array.keys():
            cursorId = f'{collection_name}/{observer_name}'
            self.cursors_array[collection_name][observer_name] = \
                { 'cursor':cursor, 'type':observer_type}
        else:
            self.cursors_array[f'{collection_name}'] = \
                {
                    observer_name:{'cursor':cursor,
                                   'type':observer_type}
                 }
            cursorId = f'{collection_name}/{observer_name}'

        print('p1.5', flush=True)
        return cursorId

    def watch(self, collection_name: str, observer_name: str):
        self.__check_parameters(collection_name, observer_name)
        collection = self.database[collection_name]
        cursor_data = self.cursors_array[collection_name][observer_name]

        if (cursor_data['type'] == Constants.OBSERVER_TYPE_WAIT or
                cursor_data['type'] == ''):
            try:
                metadata_query = {"_id": 0}
                dataset_metadata = collection.find_one(metadata_query)
                if dataset_metadata["finished"]:
                    return dataset_metadata
            except:
                pass

        return cursor_data["cursor"].next()['fullDocument']


    def remove_watch(self, collection_name: str, observer_name: str):
        self.__check_parameters(collection_name, observer_name)
        cursor_data = self.cursors_array[collection_name][observer_name]

        cursor_data["cursor"].close()
        self.cursors_array[collection_name].pop(observer_name)

    def __get_default_observer_name(self, collection_name: str) -> str:
        if collection_name not in self.cursors_array:
            index = 0
            skip = True
        else:
            index = len(self.cursors_array[collection_name])
            skip = False

        observer_name = f'{Constants.DEFAULT_OBSERVER_NAME_PREFIX}{index}'
        if skip:
            return observer_name

        cn = 0
        while observer_name in self.cursors_array[collection_name].keys():
            cn += 1
            observer_name = f'{Constants.DEFAULT_OBSERVER_NAME_PREFIX}' \
                            f'{index+cn}'

        return observer_name


    def __check_parameters(self, collection_name: str, observer_name: str) \
            -> None:
        if collection_name not in self.database.list_collection_names():
            raise KeyError(f'the collection "{collection_name}" does not '
                           f'exist in the database')
        if collection_name not in self.cursors_array.keys():
            raise KeyError(f'the collection "{collection_name}" has no '
                           f'observers assigned to it')
        if observer_name not in self.cursors_array[collection_name].keys():
            raise KeyError(f'invalid observer name for collection '
                           f'"{collection_name}"')


    def get_observer_data(self, collection_name: str, observer_name: int) \
            -> dict:
        return self.cursors_array[collection_name][observer_name]


    def insert_one_in_file(self, filename: str, json_object: dict) -> None:
        file_collection = self.database[filename]
        file_collection.insert_one(json_object)
