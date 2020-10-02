# Database API microservice

The Database API microservice creates a level of abstraction through a REST API. Using MongoDB, datasets are downloaded in CSV format and parsed into JSON format where the primary key for each document is the filename field contained in the JSON file POST request.

## GUI tool to handle database files
There are GUI tools to handle database files, for example, [NoSQLBooster](https://nosqlbooster.com) can interact with mongoDB used in database, and makes several tasks which are limited in `learning\_orchestra\_client package`, as schema visualization and files extraction and download to formats as CSV, JSON, you also can navigate in all inserted files in easy way and visualize each row from determined file, to use this tool connect with the url `cluster\_ip:27017` and use the credentials
```
username = root
password = owl45#21
```

## List all inserted files
`GET CLUSTER_IP:5000/files`

Returns an array of metadata files from the database, where each file contains a metadata file.

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

* `fields` - Names of the columns in the file
* `filename` - Name of the file
* `finished` - Flag used to indicate if asynchronous processing from file downloader is finished
* `time_created` - Time of creation
* `url` - URL used to download the file

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

* `parent_filename` - The `filename` used to make a preprocess task, from which the current file is derived.

### Classifier prediction files metadata

```json
{
    "F1": "0.7030995388400528",
    "accuracy": "0.7034883720930233",
    "classificator": "nb",
    "filename": "titanic_testing_new_prediction_nb",
    "fit_time": 41.870062828063965
}
```

* `F1` - F1 Score from model accuracy
* `accuracy` - Accuracy rate from model prediction
* `classificator` - Initials from used classificator
* `filename` - Name of the file 
* `fit_time` - Time taken for the model to be fit during training

## List file content

`GET CLUSTER_IP:5000/files/<filename>?skip=number&limit=number&query={}`

Returns rows of the file requested, with pagination

* `filename` - Name of file requests
* `skip` - Amount of lines to skip in the CSV file
* `limit` - Limit the query result, maximum limit set to 20 rows
* `query` - Query to find documents, if only pagination is requested, `query` should be empty curly brackets `query={}`

The first row in the query is always the metadata file.

## Post file

`POST CLUSTER_IP:5000/files`

Insert a CSV into the database using the POST method, JSON must be contained in the body of the HTTP request.
The following fields are required: 
```json
{
    "filename": "key_to_document_identification",
    "url": "http://sitetojson.file/path/to/csv"
}
```

## Delete an existing file
`DELETE CLUSTER_IP:5000/files/<filename>`

Request of type `DELETE`, passing the `filename` field of an existing file in the request parameters, deleting the file in the database.

