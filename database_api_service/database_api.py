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

DATABASE_URL = "DATABASE_URL"
DATABASE_PORT = "DATABASE_PORT"


class DatabaseApi:
    MESSAGE_INVALID_URL = "invalid_url"
    MESSAGE_DUPLICATE_FILE = "duplicate_file"
    MESSAGE_CREATED_FILE = "file_created"
    MESSAGE_DELETED_FILE = "deleted_file"

    def __init__(self):
        self.mongo_client = MongoClient(
                os.environ[DATABASE_URL],
                int(os.environ[DATABASE_PORT]))
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

        for file in file_collection.find(query).skip(skip).limit(limit):
            result.append(json.loads(dumps(file)))

        return result

    def delete_file(self, filename):
        file_collection = self.database[filename]
        file_collection.drop()
        return DatabaseApi.MESSAGE_DELETED_FILE

    def get_files(self):
        result = []

        for item in self.database.list_collection_names():
            result.append(item)

        return result


class FileStorage:
    DELAY_BETWEEN_STAGES = 1

    def __init__(self, filename, url, database_connection):
        self.thread_pool = ThreadPoolExecutor()
        self.filename = filename
        self.url = url
        self.database_connection = database_connection
        self.download_tratament_queue = []
        self.tratament_save_queue = []
        self.file_headers = None

    def download_file(self):
        with closing(requests.get(self.url, stream=True)) as r:
            reader = csv.reader(
                codecs.iterdecode(r.iter_lines(), encoding='utf-8'),
                delimiter=',', quotechar='"')
            self.file_headers = next(reader)
            count = 1

            for row in reader:
                self.download_tratament_queue.insert(0, row)

    def tratament_file(self):
        count = 1

        while(self.download_tratament_queue):
            downloaded_row = self.download_tratament_queue.pop()

            json_object = {self.file_headers[index]: downloaded_row[index]
                           for index
                           in range(len(self.file_headers))}

            json_object["_id"] = count
            self.tratament_save_queue.insert(0, json_object)
            count += 1

    def save_file(self):
        while(self.tratament_save_queue):
            self.database_connection.insert_one(
                self.tratament_save_queue.pop())

    def start(self):
        self.thread_pool.submit(self.download_file())
        time.sleep(self.DELAY_BETWEEN_STAGES)

        self.thread_pool.submit(self.tratament_file())
        time.sleep(self.DELAY_BETWEEN_STAGES)

        self.thread_pool.submit(self.save_file())
