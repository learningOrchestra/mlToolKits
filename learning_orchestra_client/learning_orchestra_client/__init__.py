import requests
import json
import time

cluster_url = None


class Context:
    def __init__(self, ip_from_cluster):
        global cluster_url
        cluster_url = "http://" + ip_from_cluster


class AsyncronousWait:
    WAIT_TIME = 3
    METADATA_INDEX = 0

    def wait(self, filename, pretty_response=True):
        if pretty_response:
            print("\n----------" + " WAITING " + filename + " FINISH " + "----------")

        database_api = DatabaseApi()

        while True:
            time.sleep(self.WAIT_TIME)
            response = database_api.read_file(filename, limit=1, pretty_response=False)

            if len(response["result"]) == 0:
                continue

            if response["result"][self.METADATA_INDEX]["finished"]:
                break


class ResponseTreat:
    HTTP_CREATED = 201
    HTTP_SUCESS = 200
    HTTP_ERROR = 500

    def treatment(self, response, pretty_response=True):
        if response.status_code >= self.HTTP_ERROR:
            return response.text
        elif (
            response.status_code != self.HTTP_SUCESS
            and response.status_code != self.HTTP_CREATED
        ):
            raise Exception(response.json()["result"])
        else:
            if pretty_response:
                return json.dumps(response.json(), indent=2)
            else:
                return response.json()


class DatabaseApi:
    DATABASE_API_PORT = "5000"

    def __init__(self):
        global cluster_url
        self.url_base = cluster_url + ":" + self.DATABASE_API_PORT + "/files"
        self.asyncronous_wait = AsyncronousWait()

    def read_resume_files(self, pretty_response=True):
        if pretty_response:
            print("\n----------" + " READ RESUME FILES " + "----------")

        url = self.url_base
        response = requests.get(url)

        return ResponseTreat().treatment(response, pretty_response)

    def read_file(self, filename, skip=0, limit=10, query={}, pretty_response=True):
        if pretty_response:
            print("\n----------" + " READ FILE " + filename + " ----------")

        request_params = {"skip": str(skip), "limit": str(limit), "query": str(query)}
        read_file_url = self.url_base + "/" + filename
        response = requests.get(url=read_file_url, params=request_params)

        return ResponseTreat().treatment(response, pretty_response)

    def create_file(self, filename, url, pretty_response=True):
        if pretty_response:
            print("\n----------" + " CREATE FILE " + filename + " ----------")

        request_body_content = {"filename": filename, "url": url}

        response = requests.post(url=self.url_base, json=request_body_content)

        return ResponseTreat().treatment(response, pretty_response)

    def delete_file(self, filename, pretty_response=True):
        if pretty_response:
            print("\n----------" + " DELETE FILE " + filename + " ----------")

        self.asyncronous_wait.wait(filename, pretty_response)

        request_url = self.url_base + "/" + filename
        response = requests.delete(url=request_url)

        return ResponseTreat().treatment(response, pretty_response)


class Projection:
    PROJECTION_PORT = "5001"

    def __init__(self):
        global cluster_url
        self.url_base = cluster_url + ":" + self.PROJECTION_PORT + "/projections"

        self.asyncronous_wait = AsyncronousWait()

    def create_projection(
        self, filename, projection_filename, fields, pretty_response=True
    ):
        if pretty_response:
            print(
                "\n----------"
                + " CREATE PROJECTION FROM "
                + filename
                + " TO "
                + projection_filename
                + " ----------"
            )

        self.asyncronous_wait.wait(filename, pretty_response)

        request_body_content = {
            "projection_filename": projection_filename,
            "fields": fields,
        }
        request_url = self.url_base + "/" + filename
        response = requests.post(url=request_url, json=request_body_content)

        return ResponseTreat().treatment(response, pretty_response)


class Histogram:
    HISTOGRAM_PORT = "5004"

    def __init__(self):
        global cluster_url
        self.url_base = cluster_url + ":" + self.HISTOGRAM_PORT + "/histograms"

        self.asyncronous_wait = AsyncronousWait()

    def create_histogram(
        self, filename, histogram_filename, fields, pretty_response=True
    ):
        if pretty_response:
            print(
                "\n----------"
                + " CREATE HISTOGRAM FROM "
                + filename
                + " TO "
                + histogram_filename
                + " ----------"
            )

        self.asyncronous_wait.wait(filename, pretty_response)

        request_body_content = {
            "histogram_filename": histogram_filename,
            "fields": fields,
        }
        request_url = self.url_base + "/" + filename
        response = requests.post(url=request_url, json=request_body_content)

        return ResponseTreat().treatment(response, pretty_response)


class Tsne:
    TSNE_PORT = "5005"

    def __init__(self):
        global cluster_url
        self.url_base = cluster_url + ":" + self.TSNE_PORT + "/images"

        self.asyncronous_wait = AsyncronousWait()

    def create_image_plot(
        self, tsne_filename, parent_filename, label_name=None, pretty_response=True
    ):
        if pretty_response:
            print(
                "\n----------"
                + " CREATE t-SNE IMAGE PLOT FROM "
                + parent_filename
                + " TO "
                + tsne_filename
                + " ----------"
            )

        self.asyncronous_wait.wait(parent_filename, pretty_response)

        request_body_content = {
            "tsne_filename": tsne_filename,
            "label_name": label_name,
        }
        request_url = self.url_base + "/" + parent_filename
        response = requests.post(url=request_url, json=request_body_content)

        return ResponseTreat().treatment(response, pretty_response)

    def delete_image_plot(self, tsne_filename, pretty_response=True):
        if pretty_response:
            print(
                "\n----------"
                + " DELETE "
                + tsne_filename
                + "  t-SNE IMAGE PLOT "
                + "----------"
            )

        request_url = self.url_base + "/" + tsne_filename
        response = requests.delete(url=request_url)

        return ResponseTreat().treatment(response, pretty_response)

    def read_image_plot_filenames(self, pretty_response=True):
        if pretty_response:
            print("\n---------- READE IMAGE PLOT FILENAMES " + " ----------")

        request_url = self.url_base
        response = requests.get(url=request_url)

        return ResponseTreat().treatment(response, pretty_response)

    def read_image_plot(self, tsne_filename, pretty_response=True):
        if pretty_response:
            print(
                "\n----------"
                + " READ "
                + tsne_filename
                + " t-SNE IMAGE PLOT "
                + "----------"
            )

        request_url = self.url_base + "/" + tsne_filename
        return request_url


class Pca:
    PCA_PORT = "5006"

    def __init__(self):
        global cluster_url
        self.url_base = cluster_url + ":" + self.PCA_PORT + "/images"

        self.asyncronous_wait = AsyncronousWait()

    def create_image_plot(
        self, pca_filename, parent_filename, label_name=None, pretty_response=True
    ):
        if pretty_response:
            print(
                "\n----------"
                + " CREATE PCA IMAGE PLOT FROM "
                + parent_filename
                + " TO "
                + pca_filename
                + " ----------"
            )

        self.asyncronous_wait.wait(parent_filename, pretty_response)

        request_body_content = {"pca_filename": pca_filename, "label_name": label_name}
        request_url = self.url_base + "/" + parent_filename
        response = requests.post(url=request_url, json=request_body_content)

        return ResponseTreat().treatment(response, pretty_response)

    def delete_image_plot(self, pca_filename, pretty_response=True):
        if pretty_response:
            print(
                "\n----------"
                + " DELETE "
                + pca_filename
                + " PCA IMAGE PLOT "
                + "----------"
            )

        request_url = self.url_base + "/" + pca_filename
        response = requests.delete(url=request_url)

        return ResponseTreat().treatment(response, pretty_response)

    def read_image_plot_filenames(self, pretty_response=True):
        if pretty_response:
            print("\n---------- READE IMAGE PLOT FILENAMES " + " ----------")

        request_url = self.url_base
        response = requests.get(url=request_url)

        return ResponseTreat().treatment(response, pretty_response)

    def read_image_plot(self, pca_filename, pretty_response=True):
        if pretty_response:
            print(
                "\n----------"
                + " READ "
                + pca_filename
                + " PCA IMAGE PLOT "
                + "----------"
            )

        request_url = self.url_base + "/" + pca_filename
        return request_url


class DataTypeHandler:
    DATA_TYPE_HANDLER_PORT = "5003"

    def __init__(self):
        global cluster_url
        self.url_base = cluster_url + ":" + self.DATA_TYPE_HANDLER_PORT + "/fieldtypes"
        self.asyncronous_wait = AsyncronousWait()

    def change_file_type(self, filename, fields_dict, pretty_response=True):
        if pretty_response:
            print("\n----------" + " CHANGE " + filename + " FILE TYPE " + "----------")

        self.asyncronous_wait.wait(filename, pretty_response)

        url_request = self.url_base + "/" + filename

        response = requests.patch(url=url_request, json=fields_dict)

        return ResponseTreat().treatment(response, pretty_response)


class Model:
    MODEL_BUILDER_PORT = "5002"

    def __init__(self):
        global cluster_url
        self.url_base = cluster_url + ":" + self.MODEL_BUILDER_PORT + "/models"
        self.asyncronous_wait = AsyncronousWait()

    def create_model(
        self,
        training_filename,
        test_filename,
        preprocessor_code,
        model_classificator,
        pretty_response=True,
    ):
        if pretty_response:
            print(
                "\n----------"
                + " CREATE MODEL WITH "
                + training_filename
                + " AND "
                + test_filename
                + " ----------"
            )

        self.asyncronous_wait.wait(training_filename, pretty_response)
        self.asyncronous_wait.wait(test_filename, pretty_response)

        request_body_content = {
            "training_filename": training_filename,
            "test_filename": test_filename,
            "preprocessor_code": preprocessor_code,
            "classificators_list": model_classificator,
        }

        response = requests.post(url=self.url_base, json=request_body_content)

        return ResponseTreat().treatment(response, pretty_response)
