import codecs
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from datetime import datetime
import pytz
from contextlib import closing
import csv
from pymongo import MongoClient, ASCENDING
import requests


class Database:
    DATABASE_URL = "DATABASE_URL"
    DATABASE_PORT = "DATABASE_PORT"
    ROW_ID = "_id"

    def __init__(self, database_url, replica_set, database_port, database_name):
        self.mongo_client = MongoClient(
            database_url + '/?replicaSet=' + replica_set, int(database_port))
        self.database = self.mongo_client[database_name]

    def connection(self, filename):
        return self.database[filename]

    def find_in_file(self, filename, query, skip=0, limit=1):
        file_collection = self.database[filename]
        return (
            file_collection.find(query).sort(self.ROW_ID, ASCENDING).skip(
                skip).limit(limit)
        )

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


class Csv:
    MAX_QUEUE_SIZE = 1000
    MAX_NUMBER_THREADS = 3
    FINISHED = "finished"
    file_headers = None
    ROW_ID = "_id"
    METADATA_ROW_ID = 0

    def __init__(self, database_connection):
        self.database_connection = database_connection
        self.thread_pool = ThreadPoolExecutor(
            max_workers=self.MAX_NUMBER_THREADS)
        self.download_treatment_queue = Queue(maxsize=self.MAX_QUEUE_SIZE)
        self.treatment_save_queue = Queue(maxsize=self.MAX_QUEUE_SIZE)

    def save_file(self, filename, url):
        print("teste2", flush=True)

        Csv.validate_url(url)
        self.create_metadata_file(filename, url)

        self.thread_pool.submit(self.download_row, url)
        self.thread_pool.submit(self.treat_row)
        self.thread_pool.submit(self.save_row, filename)

    def download_row(self, url):
        with closing(requests.get(url, stream=True)) as response:
            reader = csv.reader(
                codecs.iterdecode(response.iter_lines(), encoding="utf-8"),
                delimiter=",",
                quotechar='"',
            )
            self.file_headers = next(reader)
            for row in reader:
                self.download_treatment_queue.put(row)
        self.download_treatment_queue.put(self.FINISHED)

    def treat_row(self):
        row_count = 1
        while True:
            downloaded_row = self.download_treatment_queue.get()
            if downloaded_row == self.FINISHED:
                break
            json_object = {
                self.file_headers[index]: downloaded_row[index]
                for index in range(len(self.file_headers))
            }
            json_object[self.ROW_ID] = row_count
            self.treatment_save_queue.put(json_object)
            row_count += 1
        self.treatment_save_queue.put(self.FINISHED)

    def save_row(self, filename):
        while True:
            json_object = self.treatment_save_queue.get()
            if json_object == self.FINISHED:
                break
            self.database_connection.insert_one_in_file(filename, json_object)

        self.update_medata_finished_flag(filename, True)

    def create_metadata_file(self, filename, url):
        timezone_london = pytz.timezone("Etc/Greenwich")
        london_time = datetime.now(timezone_london)

        metadata_file = {
            "datasetName": filename,
            "url": url,
            "timeCreated": london_time.strftime("%Y-%m-%dT%H:%M:%S-00:00"),
            self.ROW_ID: self.METADATA_ROW_ID,
            self.FINISHED: False,
            "fields": "processing",
            "type": "dataset"
        }
        self.database_connection.insert_one_in_file(filename, metadata_file)

    def update_medata_finished_flag(self, filename, flag):
        self.database_connection.update_one_in_file(
            filename,
            {self.ROW_ID: self.METADATA_ROW_ID},
            {"$set": {self.FINISHED: flag, "fields": self.file_headers}},
        )

    @staticmethod
    def validate_url(url):
        response = requests.head(url)
        response_content_type = response.headers.get("content-type")

        print("teste", flush=True)
        print(response_content_type, flush=True)
        allowed_contents_type = ["application/x-download",
                                 "text/csv",
                                 "text/plain"]
        if response_content_type not in allowed_contents_type:
            raise requests.exceptions.RequestException
