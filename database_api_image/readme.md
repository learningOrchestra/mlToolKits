# database

The database system has 4 services, the database_primary, database_secondary and database_arbiter, which uses an bitnami image of mongodb on DockerHub to host the database, this services work to database replication, in case of database_primary service fall, the database_secondary service will respond all read operations, the database_arbiter service will setting replication in database_primary and database_secondary services. There is a database API service (database_api), where it is created a level of abstraction through a REST API to use the database.

# database_api service
Documents are downloaded in csv and handled in json format, the primary key for each document is the filename field contained in the sent json file.

## GET /files
Return an array of metadata files in database.
```
{
	"filename": "key_to_document_identification",
	"finished": true,
	"url": "http://sitetojson.file/path/to/csv"
}
```

## GET /files/<filename\>?skip=number&limit=number&query={}
Return rows of filename, and paginate in query result

* filename - filename of inserted file
* skip - amount lines to skip in csv file
* limit - limit of returned query result, max limit setted in 20 rows
* query - query to find documents, if use method only to paginate, use blank json, as {}

The first row is the metadata file, metadata contain the fields:
```
{

	"_id": 0,
	"filename": "key_to_document_identification",
	"finished": true or false,
	"url": "http://sitetojson.file/path/to/csv",
	"time_created": "creation time of file"   
}
```

If metadata file belong to preprocessed filename, there are the fields:

```
{

	"_id": 0,
	"filename": "key_to_document_identification",
	"finished": true or false,
	"parent_filename": "filename used to preprocessing",
	"time_created": "creation time of file"
}
```
## POST /files
Insert a csv into the database via path /add using the POST method, json must be contained in the body of the http request.
The inserted json must contained the fields: 
```
{
  filename: "key_to_document_identification",
  url: "http://sitetojson.file/path/to/csv"
}
```

## DELETE /files/<filename\>
Request of type DELETE, informing the value of file's filename field in argument request, deleting the database file, if one exists with that value.

