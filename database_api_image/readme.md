# database

The database system has 4 services, the database_primary, database_secondary and database_arbiter, which uses an bitnami image of mongodb on DockerHub to host the database, this services work to database replication, in case of database_primary service fall, the database_secondary service will respond all read operations, the database_arbiter service will setting replication in database_primary and database_secondary services. There is a database API service (database_api), where it is created a level of abstraction through a REST API to use the database.

# database_api service
Documents are downloaded in csv and handled in json format, the primary key for each document is the filename field contained in the sent json file.

## GET IP:5000/files
Return an array of metadata files in database, each file inserted in database contains a metadata file.

Downloaded files:
```
{
    "fields": [
        "PassengerId",
        "Survived",
        "Pclass",
        "Name",
        "Sex",
        "Age",
        "SibSp",
        "Parch",
        "Ticket",
        "Fare",
        "Cabin",
        "Embarked"
    ],
    "filename": "titanic_training",
    "finished": true,
    "time_created": "2020-07-28T22:16:10-00:00",
    "url": "https://filebin.net/rpfdy8clm5984a4c/titanic_training.csv?t=gcnjz1yo"
}
```
Preprocessed files:
```
{
            "fields": [
                "PassengerId",
                "Survived",
                "Pclass",
                "Name",
                "Sex",
                "Age",
                "SibSp",
                "Parch",
                "Embarked"
            ],
            "filename": "titanic_training_projection",
            "finished": false,
            "parent_filename": "titanic_training",
            "time_created": "2020-07-28T12:01:44-00:00"
        }
```

Classificator prediction files:

```
{
    "accuracy": "1.0",
    "classificator": "gb",
    "error": "0.0",
    "filename": "titanic_testing_900_prediction_gb",
    "fit_time": 69.43671989440918
}
```

## GET IP:5000/files/<filename\>?skip=number&limit=number&query={}
Return rows of filename, and paginate in query result

* filename - filename of inserted file
* skip - amount lines to skip in csv file
* limit - limit of returned query result, max limit setted in 20 rows
* query - query to find documents, if use method only to paginate, use blank json, as {}

The first row is always the metadata file

## POST IP:5000/files
Insert a csv into the database via path /add using the POST method, json must be contained in the body of the http request.
The inserted json must contained the fields: 
```
{
  filename: "key_to_document_identification",
  url: "http://sitetojson.file/path/to/csv"
}
```

## DELETE IP:5000/files/<filename\>
Request of type DELETE, informing the value of file's filename field in argument request, deleting the database file, if one exists with that value.

