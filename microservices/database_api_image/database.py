from bson.json_util import dumps
import json
import codecs
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from constants import Constants
from contextlib import closing
import csv
import requests
import re
from utils import Database, Metadata
import os


class Storage:
    def __init__(self, database: Database):
        self.__database_connector = database

    def read_file(self, filename: str, skip: int, limit: int,
                  query: dict) -> list:
        result = []

        for file in self.__database_connector.find_in_file(
                filename, query, skip, limit
        ):
            result.append(json.loads(dumps(file)))

        return result

    def get_metadata_files(self, file_type: str) -> list:
        result = []

        for file in self.__database_connector.get_filenames():
            metadata_file = self.__database_connector.find_one_in_file(
                file,
                {Constants.ROW_ID: Constants.METADATA_ROW_ID,
                 Constants.TYPE_FIELD_NAME: file_type}
            )
            if metadata_file is None:
                continue
            metadata_file.pop(Constants.ROW_ID)
            result.append(metadata_file)

        return result

    def save_file(self, filename: str, url: str) -> None:
        pass

    def delete_file(self, filename) -> None:
        pass


class Generic(Storage):
    def __init__(self, database_connector: Database,
                 metadata_creator: Metadata):
        super().__init__(database_connector)
        self.__metadata_creator = metadata_creator
        self.__database_connector = database_connector

    def save_file(self, filename: str, url: str) -> None:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            with open(self.__get_file_path(filename), 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

        self.__metadata_creator.create_file(
            filename, url, Constants.DATASET_GENERIC_TYPE)

    def delete_file(self, filename: str) -> None:
        self.__database_connector.delete_file(filename)
        os.remove(self.__get_file_path(filename))

    def __get_file_path(self, filename: str) -> str:
        return f'/{os.environ[Constants.DATASET_VOLUME_PATH]}/{filename}'


class Csv(Storage):
    __MAX_QUEUE_SIZE = 1000
    __file_headers = None

    def __init__(self, database_connector: Database,
                 metadata_creator: Metadata):
        super().__init__(database_connector)
        self.__metadata_creator = metadata_creator
        self.__database_connector = database_connector
        self.__thread_pool = ThreadPoolExecutor()
        self.__download_treatment_queue = Queue(maxsize=self.__MAX_QUEUE_SIZE)
        self.__treatment_save_queue = Queue(maxsize=self.__MAX_QUEUE_SIZE)

    def save_file(self, filename: str, url: str) -> None:
        self.__metadata_creator.create_file(
            filename, url, Constants.DATASET_CSV_TYPE)

        self.__thread_pool.submit(self.__download_row, url)
        self.__thread_pool.submit(self.__treat_row)
        self.__thread_pool.submit(self.__save_row, filename)

    def delete_file(self, filename) -> None:
        self.__database_connector.delete_file(filename)

    def __download_row(self, url: str) -> None:
        with closing(requests.get(url, stream=True)) as response:
            reader = csv.reader(
                codecs.iterdecode(response.iter_lines(), encoding="utf-8"),
                delimiter=",",
                quotechar='"',
            )
            untreated_headers = next(reader)
            self.__file_headers = [re.sub('\W+', '', column) for column in
                                   untreated_headers]
            for row in reader:
                self.__download_treatment_queue.put(row)
        self.__download_treatment_queue.put(Constants.FINISHED)

    def __treat_row(self) -> None:
        row_count = 1
        while True:
            downloaded_row = self.__download_treatment_queue.get()
            if downloaded_row == Constants.FINISHED:
                break
            json_object = {
                self.__file_headers[index]: downloaded_row[index]
                for index in range(len(self.__file_headers))
            }
            json_object[Constants.ROW_ID] = row_count
            self.__treatment_save_queue.put(json_object)
            row_count += 1
        self.__treatment_save_queue.put(Constants.FINISHED)

    def __save_row(self, filename: str) -> None:
        while True:
            json_object = self.__treatment_save_queue.get()
            if json_object == Constants.FINISHED:
                break
            self.__database_connector.insert_one_in_file(
                filename, json_object)

        self.__metadata_creator.update_file_headers(
            filename,
            self.__file_headers
        )
        self.__metadata_creator.update_finished_flag(filename, True)


class Dataset:
    def __init__(self, file_manager: Storage):
        self.__file_manager = file_manager

    def add_file(self, url: str, filename: str) -> None:
        self.__file_manager.save_file(filename, url)

    def delete_file(self, filename: str) -> None:
        self.__file_manager.delete_file(filename)

    def read_file(self, filename: str, skip: int, limit: int,
                  query: dict) -> list:
        return self.__file_manager.read_file(filename, skip, limit, query)

    def get_metadata_files(self, file_type: str) -> list:
        return self.__file_manager.get_metadata_files(file_type)
