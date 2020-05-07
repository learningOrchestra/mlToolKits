# database

The database system has 4 services, the database_primary, database_secondary and database_arbiter, which uses an bitnami image of mongodb on DockerHub to host the database, this services work to database replication, in case of database_primary service fall, the database_secondary service will respond all read operations, the database_arbiter service will setting replication in database_primary and database_secondary services. There is a database API service (database_api), where it is created a level of abstraction through a REST API to use the database.

# database_api service
Documents are handled in json format, the primary key for each document being the filename field contained in the sent json file.
## POST /add
Insert a json into the database via path / add using the POST method, json must be contained in the body of the http request.
The inserted json must contained the fields: \
```
{
  filename: "key_to_document_identification",
  url: "http://sitetojson.file/path/to/json"
}
```
## GET /files
Returns all files inserted in the database.
## GET /file/filename
A request with the value of the file's filename field, returning the file if there is one with a given value.
## DELETE /file/filename
Request of type DELETE, informing the value of the file's filename field, excluding the database file, if one exists with a given value.
