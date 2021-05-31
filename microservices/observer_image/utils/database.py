from typing import Union

from pymongo import MongoClient, errors
from pymongo.change_stream import CollectionChangeStream


class Database:

    def __init__(self, database_url: str, replica_set: str, database_port: int,
                 database_name: str):

        self.mongo_client = MongoClient(
            f'{database_url}', int(database_port),
            replicaSet=replica_set
        )

        self.database = self.mongo_client[database_name]
        self.cursors_array = dict()

    def watch(self, collection_name: str, pipeline: []) -> str:
        collection = self.database[collection_name]

        cursor = collection.watch(
            pipeline=pipeline,
            full_document='updateLookup'
        )

        if f'{collection_name}' in self.cursors_array is list:
            size_of_cursors = len(self.cursors_array[f'{collection_name}'])
            cursor_name = f'{collection_name}-{size_of_cursors}'
            self.cursors_array[f'{collection_name}'].append(
                cursor)
            return cursor_name

        cursor_name = f'{collection_name}-{0}'
        self.cursors_array[f'{collection_name}'] = [
            cursor
        ]

        return cursor_name

    def remove_watch(self, collection_name: str):
        col_name, index = collection_name.split('-')
        cursor = self.cursors_array[f'{col_name}'][int(index)]
        cursor.close()

    def get_cursor(self, collection_name: str) \
            -> CollectionChangeStream:
        col_name, index = collection_name.split('-')
        return self.cursors_array[f'{col_name}'][int(index)]

    def insert_one_in_file(self, filename: str, json_object: dict) -> None:
        file_collection = self.database[filename]
        file_collection.insert_one(json_object)
