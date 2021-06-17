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

    def submit(self, collection_name: str, pipeline: [], timeout: int=0) -> str:
        if collection_name not in self.database.list_collection_names():
            raise KeyError

        collection_data = {
            "pipeline":pipeline,
            "timeout":timeout
        }

        print('a3', flush=True)
        if collection_name in self.cursors_array.keys():
            cursorId = f'{collection_name}?index=' \
                       f'{len(self.cursors_array[collection_name])}'
            self.cursors_array[collection_name].append(collection_data)
        else:
            self.cursors_array[f'{collection_name}'] = [collection_data]
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

        try:
            metadata_query = {"_id": 0}
            dataset_metadata = collection.find_one(metadata_query)
            if dataset_metadata["finished"]:
                return dataset_metadata
        except:
            pass

        cursor_data = self.cursors_array[collection_name][observer_index]
        timeout = cursor_data["timeout"]
        pipeline = cursor_data["pipeline"]
        timeout = timeout * self.__TIMEOUT_TIME_MULTIPLICATION \
            if timeout>0 else None

        if "cursor" in cursor_data:
            return cursor_data["cursor"].next()

        print("----------->a1",flush=True)
        collection["cursor"] = collection.watch(
            pipeline=pipeline,
            full_document='updateLookup'
        )
        print("----------->a2",flush=True)

        return collection["cursor"].next()


    def remove_watch(self, collection_name: str, observer_index: int):
        collection = self.cursors_array[collection_name][observer_index]

        if "cursor" in collection:
            collection["cursor"].close()

        self.cursors_array.pop(collection_name)

    def get_observer_data(self, collection_name: str, observer_index: int) \
            -> dict:
        return self.cursors_array[collection_name][observer_index]

    def insert_one_in_file(self, filename: str, json_object: dict) -> None:
        file_collection = self.database[filename]
        file_collection.insert_one(json_object)
