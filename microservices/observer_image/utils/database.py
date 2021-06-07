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
        if collection_name not in self.database:
            raise KeyError

        if collection_name in self.cursors_array.keys():
            cursorId = f'{collection_name}?index=' \
                       f'{len(self.cursors_array[collection_name])}'
            self.cursors_array[collection_name].append({
                "pipeline":pipeline,
                "timeout":timeout
            })
        else:
            self.cursors_array[f'{collection_name}'] = [{
                "pipeline":pipeline,
                "timeout":timeout
            }]
            cursorId = f'{collection_name}?index=0'

        return cursorId

    def watch(self, collection_name: str, observer_index: int=0):
        try:
            collection = self.database[collection_name][observer_index]
        except KeyError:
            raise KeyError('collection not found')
        except IndexError:
            raise IndexError('observer index not found')

        timeout = collection["timeout"]
        pipeline = collection["pipeline"]
        timeout = timeout * self.__TIMEOUT_TIME_MULTIPLICATION \
            if timeout>0 else None

        if "cursor" in collection:
            return collection["cursor"].next()

        with collection.watch(
            pipeline=pipeline,
            full_document='updateLookup',
            max_await_time_ms=timeout
        ) as stream:
            change = stream.next()
            collection["cursor"] = stream
            return change


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
