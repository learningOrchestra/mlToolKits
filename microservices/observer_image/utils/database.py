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

    def watch(self, collection_name: str, pipeline: [], timeout: int=0) -> str:
        collection = self.database[collection_name]

        if timeout <= 0:
            cursor = collection.watch(
                pipeline=pipeline,
                full_document='updateLookup',
                max_await_time_ms=1 * self.__TIMEOUT_TIME_MULTIPLICATION
            )
        else:
            cursor = collection.watch(
                pipeline=pipeline,
                full_document='updateLookup',
                max_await_time_ms=timeout * self.__TIMEOUT_TIME_MULTIPLICATION
            )

        if collection_name in self.cursors_array.keys():
            cursorId = f'{collection_name}?index=' \
                       f'{len(self.cursors_array[collection_name])}'
            self.cursors_array[collection_name].append(cursor)
        else:
            self.cursors_array[f'{collection_name}'] = [cursor]
            cursorId = f'{collection_name}?index=0'

        return cursorId

    def remove_watch(self, collection_name: str, observer_index: int):
        cursor = self.cursors_array[collection_name][observer_index]
        cursor.close()

    def get_cursor(self, collection_name: str, observer_index: int) \
            -> CollectionChangeStream:
        return self.cursors_array[collection_name][observer_index]

    def insert_one_in_file(self, filename: str, json_object: dict) -> None:
        file_collection = self.database[filename]
        file_collection.insert_one(json_object)
