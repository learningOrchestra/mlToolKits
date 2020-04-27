# database

The database system has 2 services, the database service (database), which uses an image of the mongo on DockerHub to host the database, and the database API service (database_api), where it is created a level of abstraction through a REST API to use the database service.

# database_api
Documents are handled in json format, the primary key for each document being the filename field contained in the sent json file.
## POST /add
Insert a json into the database via path / add using the POST method, json must be contained in the body of the http request.
## GET /files
Returns all files inserted in the database.
## GET /file/filename
A request with the value of the file's filename field, returning the file if there is one with a given value.
## DELETE /file/filename
Request of type DELETE, informing the value of the file's filename field, excluding the database file, if one exists with a given value.
