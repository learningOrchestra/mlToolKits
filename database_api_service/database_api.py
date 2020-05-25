import os
from pymongo import MongoClient, errors
from bson.json_util import dumps
import requests
from contextlib import closing
import csv
import json
import codecs
import threading
from concurrent.futures import ThreadPoolExecutor, wait
import time
from queue import Queue

ROW_ID = "_id"
METADATA_ROW_ID = 0


class DatabaseApi:
    MESSAGE_INVALID_URL = "invalid_url"
    MESSAGE_DUPLICATE_FILE = "duplicate_file"
    MESSAGE_CREATED_FILE = "file_created"
    MESSAGE_DELETED_FILE = "deleted_file"
    DATABASE_URL = "DATABASE_URL"
    DATABASE_PORT = "DATABASE_PORT"

    def __init__(self):
        self.mongo_client = MongoClient(
                os.environ[self.DATABASE_URL],
                int(os.environ[self.DATABASE_PORT]))
        self.database = self.mongo_client.database

    def add_file(self, url, filename):
        try:
            file_storage = FileStorage(filename, url, self.database[filename])
            file_storage.start()

        except requests.exceptions.RequestException:
            return DatabaseApi.MESSAGE_INVALID_URL

        except errors.PyMongoError:
            return DatabaseApi.MESSAGE_DUPLICATE_FILE

        return DatabaseApi.MESSAGE_CREATED_FILE

    def read_file(self, filename, skip, limit, query):
        result = []
        file_collection = self.database[filename]

        query_object = json.loads(query)
        skip = int(skip)
        limit = int(limit)

        for file in file_collection.find(query_object).skip(skip).limit(limit):
            result.append(json.loads(dumps(file)))

        return result

    def delete_file(self, filename):
        file_collection = self.database[filename]
        file_collection.drop()
        return DatabaseApi.MESSAGE_DELETED_FILE

    def get_files(self):
        result = []

        for item in self.database.list_collection_names():
            file_collection = self.database[item]

            metadata_collection = file_collection.find_one(
                {ROW_ID: METADATA_ROW_ID})
            metadata_collection.pop(ROW_ID)

            result.append(metadata_collection)

        return result


class FileStorage:
    MAX_QUEUE_SIZE = 1000
    MAX_NUMBER_THREADS = 3
    FINISHED = "finished"

    def __init__(self, filename, url, database_connection):
        self.thread_pool = ThreadPoolExecutor(
            max_workers=self.MAX_NUMBER_THREADS)
        self.filename = filename
        self.url = url
        self.database_connection = database_connection
        self.download_tratament_queue = Queue(maxsize=self.MAX_QUEUE_SIZE)
        self.tratament_save_queue = Queue(maxsize=self.MAX_QUEUE_SIZE)
        self.file_headers = None

    def download_file(self):
        with closing(requests.get(self.url, stream=True)) as r:
            reader = csv.reader(
                codecs.iterdecode(r.iter_lines(), encoding='utf-8'),
                delimiter=',', quotechar='"')
            self.file_headers = next(reader)

            for row in reader:
                self.download_tratament_queue.put(row)

        self.download_tratament_queue.put(self.FINISHED)

    def tratament_file(self):
        row_count = 1

        while(True):
            downloaded_row = self.download_tratament_queue.get()

            if(downloaded_row == self.FINISHED):
                break

            json_object = {self.file_headers[index]: downloaded_row[index]
                           for index
                           in range(len(self.file_headers))}

            json_object[ROW_ID] = row_count

            self.tratament_save_queue.put(json_object)
            row_count += 1

        self.tratament_save_queue.put(self.FINISHED)

    def save_file(self):
        while(True):
            json_object = self.tratament_save_queue.get()

            if(json_object == self.FINISHED):
                break

            self.database_connection.insert_one(json_object)

        self.database_connection.update_one(
            {ROW_ID: METADATA_ROW_ID}, {
                '$set': {
                    self.FINISHED: True
                }})

    def start(self):
        metadata_file = {
            'filename': self.filename,
            'url': self.url,
            ROW_ID: METADATA_ROW_ID,
            self.FINISHED: False
        }
        self.database_connection.insert_one(metadata_file)

        self.thread_pool.submit(self.download_file)

        self.thread_pool.submit(self.tratament_file)

        self.thread_pool.submit(self.save_file)
