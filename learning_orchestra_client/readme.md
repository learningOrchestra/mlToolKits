# Learning Orchestra Client
This python package is created to usage with Learning Orchestra microservices

## Installation
pip install learning_orchestra_cliet

## Documentation

After downloading the package, import all classes:

`
from learning_orchestra_client import *
`

create a Context object passing a ip from your cluster in constructor parameter:

`
cluster_ip = "34.95.222.197"
Context(cluster_ip)
`

After create a Context object, you will able to usage learningOrchestra microservices.

## DatabaseApi

### `read_resume_files()`

Read all metadata files in learningOrchestra

### `read_file(self, filename_key, skip=0, limit=10, query={})`
* filename_ley : filename of file
* skip: number of rows amount to skip in pagination
* limit: number of rows to return in pagination (max setted in 20 rows per request)
* query: query to make in mongo

### `create_file(self, filename, url)`
* filename: filename of file to be created
* url: url to csv file

### `delete_file(self, filename)`
* filename: file filename to be deleted

## Projection

### `create_projection(self, filename, projection_filename, fields)`

* filename: filename of file to make projection
* projection_filename: filename used to create projection
* field: list with fields to make projection 

## DataTypeHandler

### `change_file_type(self, filename, fields_dict)`
* filenbame: filename of file
* fields_dict: dictionary with "field": "number" or field: "string" keys  

## ModelBuilder

### `build_model(self, training_filename, test_filename, label='label')`

* training_filename: filename to be used in training
* test_filename: filename to be used in test
* label: case of traning filename have a label with other name

## Example

In below there is script using the package:


    from learning_orchestra_client import *

    cluster_ip = "34.95.222.197"

    Context(cluster_ip)

    database_api = DatabaseApi()

    print(database_api.read_file("training", skip=20, limit=10))

    projection = Projection()

    print(projection.create_projection(
            "training2", "titanic_training_projection",
            ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp',
            'Parch', 'Embarked']))
    print(projection.create_projection(
            "titanic_testing_10", "titanic_testing_projection",
            ['PassengerId', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch',
            'Ticket', 'Fare', 'Embarked']))


    print(database_api.read_resume_files())
    print(database_api.delete_file("titanic_testing_10"))
    print(database_api.delete_file("titanic_training_10"))
    print(database_api.read_resume_files())
    print(database_api.create_file(
        "titanic_training_10",
        "https://filebin.net/rpfdy8clm5984a4c/titanic_training.csv?t=bg4b9hfg"))
    print(database_api.create_file(
        "titanic_testing_10",
        "https://filebin.net/mguee52ke97k0x9h/titanic_testing.csv?t=7iojj2d2"))
    print(database_api.read_file("titanic_training_10"))
    print(database_api.read_resume_files())

    projection = Projection()

    data_type_handler = DataTypeHandler()

    print(data_type_handler.change_file_type(
        "titanic_training_10", {"Survived": "number"}))

    model_builder = ModelBuilder()


    print(model_builder.build_model(
        "titanic_training_10", "titanic_testing_10", "Survived"))

    print(database_api.delete_file("titanic_testing_10"))

    print(database_api.read_resume_files())
