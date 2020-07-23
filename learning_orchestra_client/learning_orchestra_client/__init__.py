import requests
import json

cluster_url = None


class Context():
    def __init__(self, ip_from_cluster):
        global cluster_url
        cluster_url = 'http://' + ip_from_cluster


class DatabaseApi():
    DATABASE_API_PORT = "5000"

    def __init__(self):
        global cluster_url
        self.url_base = cluster_url + ':' + self.DATABASE_API_PORT + '/files'

    def read_resume_files(self):
        url = self.url_base
        return requests.get(url).json()

    def read_file(self, filename_key, skip=0, limit=10, query={}):
        request_params = {
            'skip': str(skip),
            'limit': str(limit),
            'query': str(query)
        }
        read_file_url = self.url_base + '/' + filename_key
        return requests.get(
            url=read_file_url, params=request_params).json()

    def create_file(self, filename, url):
        request_body_content = {
            'filename': filename,
            'url': url
        }

        return requests.post(url=self.url_base, json=request_body_content).\
            json()

    def delete_file(self, filename):
        request_url = self.url_base + '/' + filename
        return requests.delete(url=request_url).json()


class Projection():
    PROJECTION_PORT = "5001"

    def __init__(self):
        global cluster_url
        self.url_base = cluster_url + ':' + self.PROJECTION_PORT + \
            '/projections'

    def create_projection(self, filename, projection_filename, fields):
        request_body_content = {
            'projection_filename': projection_filename,
            'fields': fields
        }
        request_url = self.url_base + '/' + filename
        return requests.post(url=request_url, json=request_body_content).\
            json()


class DataTypeHandler():
    DATA_TYPE_HANDLER_PORT = "5003"

    def __init__(self):
        global cluster_url
        self.url_base = cluster_url + ':' + self.DATA_TYPE_HANDLER_PORT + \
            '/fieldtypes'

    def change_file_type(self, filename, fields_dict):
        url_request = self.url_base + '/' + filename

        return requests.patch(url=url_request, json=fields_dict).json()


class ModelBuilder():
    MODEL_BUILDER_PORT = '5002'

    def __init__(self):
        global cluster_url
        self.url_base = cluster_url + ':' + self.MODEL_BUILDER_PORT + '/models'

    def build_model(self, training_filename, test_filename, label='label'):
        request_body_content = {
            'training_filename': training_filename,
            'test_filename': test_filename,
            'label': label
        }

        return requests.post(url=self.url_base, json=request_body_content).\
            json()
