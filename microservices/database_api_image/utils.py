from pymongo import MongoClient, ASCENDING, cursor
import validators
from datetime import datetime
import pytz
from constants import Constants
from concurrent.futures import ThreadPoolExecutor


class Database:

    def __init__(self, url: str, replica_set: str, port: int, name: str):
        self.mongo_client = MongoClient(
            f'{url}/?replicaSet={replica_set}', port)
        self.database = self.mongo_client[name]
        self.__thread_pool = ThreadPoolExecutor()

    def find_in_file(self, filename: str, query: dict, skip: int = 0,
                     limit: int = 10) -> cursor.Cursor:
        file_collection = self.database[filename]
        return (
            file_collection.find(query).sort(Constants.ROW_ID, ASCENDING).skip(
                skip).limit(limit)
        )

    def delete_file(self, filename: str) -> None:
        file_collection = self.database[filename]
        self.__thread_pool.submit(file_collection.drop)

    def get_filenames(self) -> list:
        return self.database.list_collection_names()

    def insert_one_in_file(self, filename: str, json: dict) -> None:
        file_collection = self.database[filename]
        file_collection.insert_one(json)

    def update_one_in_file(self, filename: str, query: dict,
                           new_value: dict) -> None:
        file_collection = self.database[filename]
        file_collection.update_one(query, {"$set": new_value})

    def find_one_in_file(self, filename: str, query: dict) -> dict:
        file_collection = self.database[filename]
        return file_collection.find_one(query)


class Metadata:
    def __init__(self, database_conector: Database):
        self.__database_conector = database_conector

    def create_file(self, filename: str, url: str) -> None:
        timezone_london = pytz.timezone("Etc/Greenwich")
        london_time = datetime.now(timezone_london)

        metadata_file = {
            Constants.FILENAME_FIELD_NAME: filename,
            "url": url,
            "timeCreated": london_time.strftime("%Y-%m-%dT%H:%M:%S-00:00"),
            Constants.ROW_ID: Constants.METADATA_ROW_ID,
            Constants.FINISHED: False,
            "fields": "processing",
            Constants.TYPE_FIELD_NAME: Constants.DATASET_TYPE
        }
        self.__database_conector.insert_one_in_file(filename, metadata_file)

    def update_file_headers(self, filename: str, fields: list) -> None:
        self.__database_conector.update_one_in_file(
            filename,
            {Constants.ROW_ID: Constants.METADATA_ROW_ID},
            {"fields": fields}
        )

    def update_finished_flag(self, filename: str, flag: bool) -> None:
        self.__database_conector.update_one_in_file(
            filename,
            {Constants.ROW_ID: Constants.METADATA_ROW_ID},
            {Constants.FINISHED: flag},
        )


class UserRequest:
    __MESSAGE_INVALID_URL = "invalid url"
    __MESSAGE_DUPLICATE_FILE = "duplicated dataset name"

    def __init__(self, database_connector: Database):
        self.database = database_connector

    def filename_validator(self, filename: str) -> None:
        filenames = self.database.get_filenames()

        if filename in filenames:
            raise Exception(self.__MESSAGE_DUPLICATE_FILE)

    def csv_url_validator(self, url: str) -> None:
        if not validators.url(url):
            raise Exception(self.__MESSAGE_INVALID_URL)
