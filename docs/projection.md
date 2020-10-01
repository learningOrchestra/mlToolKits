# Projection Microservice
Projection microservice provides an api to make a projection from file inserted in database service, generating a new file and putting in database.

## Create projection from a inserted file
`POST CLUSTER_IP:5001/projections/<filename>`
Post request where `filename` is the name of the file to create a projection for.
```json
{
    "projection_filename" : "filename_to_save_projection",
    "fields" : ["list", "of", "fields"]
}
```
