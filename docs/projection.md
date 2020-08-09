# Projection microservice
Projection microservice provide an api to make a projection from file inserted in database service, generating a new file and putting in database

## Create projection from inserted file
`POST CLUSTER_IP:5001/projections/<filename>`

```json
{
    "projection_filename" : "filename_to_save_projection",
    "fields" : ["list", "of", "fields"]
}
```
