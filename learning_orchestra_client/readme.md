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

### `read_resume_files(pretty_response=True)`

Read all metadata files in learningOrchestra
* pretty_response: return indented string to visualization (default True, if False, return dict)

### `read_file(self, filename_key, skip=0, limit=10, query={}, pretty_response=True)`
* filename_ley : filename of file
* skip: number of rows amount to skip in pagination (default 0)
* limit: number of rows to return in pagination (default 10)(max setted in 20 rows per request)
* query: query to make in mongo (default empty query)
* pretty_response: return indented string to visualization (default True, if False, return dict)

### `create_file(self, filename, url, pretty_response=True)`
* filename: filename of file to be created
* url: url to csv file
* pretty_response: return indented string to visualization (default True, if False, return dict)

### `delete_file(self, filename, pretty_response=True)`
* filename: file filename to be deleted
* pretty_response: return indented string to visualization (default True, if False, return dict)

## Projection

### `create_projection(self, filename, projection_filename, fields, pretty_response=True)`

* filename: filename of file to make projection
* projection_filename: filename used to create projection
* field: list with fields to make projection 
* pretty_response: return indented string to visualization (default True, if False, return dict)

## DataTypeHandler

### `change_file_type(self, filename, fields_dict, pretty_response=True)`
* filenbame: filename of file
* fields_dict: dictionary with "field": "number" or field: "string" keys  
* pretty_response: return indented string to visualization (default True, if False, return dict)

## ModelBuilder

### `build_model(self, training_filename, test_filename, label='label', pretty_response=True)`

* training_filename: filename to be used in training
* test_filename: filename to be used in test
* label: case of traning filename have a label with other name
* pretty_response: return indented string to visualization (default True, if False, return dict)

## Example

In below there is script using the package:


    from learning_orchestra_client import *

    cluster_ip = "35.198.5.148"

    Context(cluster_ip)

    database_api = DatabaseApi()

    print(database_api.create_file(
        "titanic_training",
        "https://filebin.net/rpfdy8clm5984a4c/titanic_training.csv?t=gcnjz1yo"))
    print(database_api.create_file(
        "titanic_testing",
        "https://filebin.net/mguee52ke97k0x9h/titanic_testing.csv?t=ub4nc1rc"))

    print(database_api.read_resume_files())

    projection = Projection()

    print(projection.create_projection(
        "titanic_training", "titanic_training_projection",
        ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp',
        'Parch', 'Embarked']))
    print(projection.create_projection(
        "titanic_testing", "titanic_testing_projection",
        ['PassengerId', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch',
        'Ticket', 'Fare', 'Embarked']))

    print(database_api.delete_file("titanic_training"))
    print(database_api.delete_file("titanic_testing"))

    data_type_handler = DataTypeHandler()

    print(data_type_handler.change_file_type(
        "titanic_training_projection", {"Survived": "number"}))

    model_builder = ModelBuilder()

    print(model_builder.build_model(
        "titanic_training_projection", "titanic_testing_projection", "Survived"))