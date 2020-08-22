# Database API microservice

The Database API microservice create a level of abstraction through an REST 
API to use the database, datasets are downloaded in csv and handled in json 
format, the primary key for each document is the filename field contained in 
the sent json file from POST request.

## GUI tool to handle database files
There are GUI tools to handle database files, as example, the 
[NoSQLBooster](https://nosqlbooster.com) can interact with mongoDB used in 
database, and make several tasks which are limited in 
learning\_orchestra\_client package, as schema visualization and files 
extraction and download to formats as csv, json, you also can navigate in all 
inserted files in easy way and visualize each row from determined file, to use 
this tool, connect with the url cluster\_ip:27017 and use the user root with 
password owl45#21.

## List all inserted files
`GET CLUSTER_IP:5000/files`

Return an array of metadata files in database, each file inserted in database 
contains a metadata file.

### Downloaded files metadata 
```json
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

* fields - column names from inserted file
* filename - name to file identification
* finished - flag used to indicate if asyncronous processing from file 
downloader is finished
* time_created - creation time of file
* url - url used to file download

### Preprocessed files metadata
```json
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

* parent_filename - file filename used to make preprocessing operation

### Classificator prediction files metadata

```json
{
    "accuracy": "1.0",
    "classificator": "gb",
    "error": "0.0",
    "filename": "titanic_testing_900_prediction_gb",
    "fit_time": 69.43671989440918
}
```

* accuracy - accuracy rate from model prediction
* classificator - initials from used classificator
* error - error rate from model prediction
* fit_time - time from model fit using training dataset

## List file content

`GET CLUSTER_IP:5000/files/<filename>?skip=number&limit=number&query={}`

Return rows of filename, and paginate in query result.

* filename - filename of inserted file
* skip - amount lines to skip in csv file
* limit - limit of returned query result, max limit setted in 20 rows
* query - query to find documents, if use method only to paginate, use blank 
json, as {}

The first row is always the metadata file.

## Insert file from URL

`POST CLUSTER_IP:5000/files`

Insert a csv into the database using the POST method, json must be contained 
in the body of the http request.
The inserted json must has the fields: 
```json
{
    "filename": "key_to_document_identification",
    "url": "http://sitetojson.file/path/to/csv"
}
```

## Delete inserted file
`DELETE CLUSTER_IP:5000/files/<filename>`

Request of type DELETE, informing the value of filename field of a inserted 
file in argument request, deleting the database file, if one exist with that 
value.

