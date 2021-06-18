from typing import Union

from pymongo import MongoClient, errors
from pymongo.change_stream import CollectionChangeStream


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

    def submit(self, collection_name: str, pipeline: [], timeout: int=0,
               submit_type:str='wait') -> str:
        if collection_name not in self.database.list_collection_names():
            raise KeyError('collection not found')

        collection = self.database[collection_name]

        cursor = collection.watch(
            pipeline=pipeline,
            full_document='updateLookup',
            max_await_time_ms=timeout
        )

        print('a3', flush=True)
        if collection_name in self.cursors_array.keys():
            cursorId = f'{collection_name}?index=' \
                       f'{len(self.cursors_array[collection_name])}'
            self.cursors_array[collection_name].append({'cursor':cursor,
                                                        'type':submit_type})
        else:
            self.cursors_array[f'{collection_name}'] = [{'cursor':cursor,
                                                        'type':submit_type}]
            cursorId = f'{collection_name}?index=0'

        print('a4', flush=True)
        return cursorId

    def watch(self, collection_name: str, observer_index: int=0):
        try:
            collection = self.database[collection_name]
        except KeyError:
            raise KeyError('collection not found')

        if observer_index >= len(self.cursors_array[collection_name]):
            raise IndexError('invalid observer index')

        cursor_data = self.cursors_array[collection_name][observer_index]

        if (cursor_data['type'] == 'wait' or cursor_data['type'] == '1' or
            cursor_data['type'] == ''):
            try:
                metadata_query = {"_id": 0}
                dataset_metadata = collection.find_one(metadata_query)
                if dataset_metadata["finished"]:
                    return dataset_metadata
            except:
                pass

        return cursor_data["cursor"].next()['fullDocument']


    def remove_watch(self, collection_name: str, observer_index: int):
        cursor_data = self.cursors_array[collection_name][observer_index]

        cursor_data["cursor"].close()
        #TODO - implementar uma maneira de fazer o management dos observer index
        #self.cursors_array[collection_name].pop(observer_index)

    def get_observer_data(self, collection_name: str, observer_index: int) \
            -> dict:
        return self.cursors_array[collection_name][observer_index]

    def insert_one_in_file(self, filename: str, json_object: dict) -> None:
        file_collection = self.database[filename]
        file_collection.insert_one(json_object)
