import os
from pymongo import MongoClient, errors, ASCENDING, DESCENDING
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
from datetime import datetime
import pytz

ROW_ID = "_id"
METADATA_ROW_ID = 0


class DatabaseApi:
    MESSAGE_INVALID_URL = "invalid_url"
    MESSAGE_DUPLICATE_FILE = "duplicate_file"

    def __init__(self, database_object, file_manager_object):
        self.database_object = database_object
        self.file_manager_object = file_manager_object

    def add_file(self, url, filename):
        try:
            file_storage = self.file_manager_object.storage_file(
                filename, url, self.database_object)

        except requests.exceptions.RequestException:
            raise Exception(self.MESSAGE_INVALID_URL)

        except errors.PyMongoError:
            raise Exception(self.MESSAGE_DUPLICATE_FILE)

    def read_file(self, filename, skip, limit, query):
        result = []

        query_object = json.loads(query)
        skip = int(skip)
        limit = int(limit)

        for file in self.database_object.find_in_file(
                                                      filename, query_object,
                                                      skip, limit):
            result.append(json.loads(dumps(file)))

        return result

    def delete_file(self, filename):
        self.database_object.delete_file(filename)

    def get_files(self):
        result = []
        skip_result = 0
        limit_result = 0

        for file in self.database_object.get_filenames():

            metadata_file = self.database_object.find_one_in_file(
                file, {ROW_ID: METADATA_ROW_ID})

            metadata_file.pop(ROW_ID)
            result.append(metadata_file)

        return result


class DatabaseInterface():
    def connection(self, filename):
        pass

    def find_in_file(self, filename, query, skip, limit):
        pass

    def delete_file(self, filename):
        pass

    def find_one_in_file(self, filename, query):
        pass

    def get_filenames(self):
        pass

    def insert_one_in_file(self, filename, json_object):
        pass

    def update_one_in_file(self, filename, new_value, query):
        pass


class CsvManagerInterface():
    def storage_file(self, filename, url, database_connection):
        pass


class MongoOperations(DatabaseInterface):
    DATABASE_URL = "DATABASE_URL"
    DATABASE_PORT = "DATABASE_PORT"

    def __init__(self):
        self.mongo_client = MongoClient(
            os.environ[self.DATABASE_URL],
            int(os.environ[self.DATABASE_PORT]))
        self.database = self.mongo_client.database

    def connection(self, filename):
        return self.database[filename]

    def find_in_file(self, filename, query, skip=0, limit=1):
        file_collection = self.database[filename]
        return file_collection.find(query).sort(
            ROW_ID, ASCENDING).skip(skip).limit(limit)

    def delete_file(self, filename):
        file_collection = self.database[filename]
        file_collection.drop()

    def get_filenames(self):
        return self.database.list_collection_names()

    def insert_one_in_file(self, filename, json_object):
        file_collection = self.database[filename]
        file_collection.insert_one(json_object)

    def update_one_in_file(self, filename, new_value, query):
        file_collection = self.database[filename]
        file_collection.update_one(new_value, query)

    def find_one_in_file(self, filename, query):
        file_collection = self.database[filename]
        return file_collection.find_one(query)


class CsvDownloader(CsvManagerInterface):
    MAX_QUEUE_SIZE = 1000
    MAX_NUMBER_THREADS = 3
    FINISHED = "finished"
    file_headers = None

    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(
            max_workers=self.MAX_NUMBER_THREADS)
        self.download_tratament_queue = Queue(maxsize=self.MAX_QUEUE_SIZE)
        self.tratament_save_queue = Queue(maxsize=self.MAX_QUEUE_SIZE)

    def download_file(self, url):
        with closing(requests.get(url, stream=True)) as r:

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

    def save_file(self, database_connection, filename):
        while(True):
            json_object = self.tratament_save_queue.get()

            if(json_object == self.FINISHED):
                break

            database_connection.insert_one_in_file(filename, json_object)

        database_connection.update_one_in_file(
            filename,
            {ROW_ID: METADATA_ROW_ID}, {
                '$set': {
                    self.FINISHED: True,
                    'fields': self.file_headers
                }})

    def validate_csv_url(self, url):
        with closing(requests.get(url, stream=True)) as r:

            reader = csv.reader(
                codecs.iterdecode(r.iter_lines(), encoding='utf-8'),
                delimiter=',', quotechar='"')

            first_line = next(reader)

            first_symbol_html = '<'
            first_symbol_json = '{'

            if(first_line[0][0] == first_symbol_html or
               first_line[0][0] == first_symbol_json):
                raise requests.exceptions.RequestException

    def storage_file(self, filename, url, database_connection):
        self.validate_csv_url(url)

        timezone_london = pytz.timezone('Etc/Greenwich')
        london_time = datetime.now(timezone_london)

        metadata_file = {
            'filename': filename,
            'url': url,
            'time_created': london_time.strftime("%Y-%m-%dT%H:%M:%S-00:00"),
            ROW_ID: METADATA_ROW_ID,
            self.FINISHED: False,
            'fields': "processing"
        }
        database_connection.insert_one_in_file(filename, metadata_file)

        self.thread_pool.submit(self.download_file, url)

        self.thread_pool.submit(self.tratament_file)

        self.thread_pool.submit(
            self.save_file, database_connection, filename)
