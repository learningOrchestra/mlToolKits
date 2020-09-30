# Data Type Handler microservice
This Microservice changes data type from stored file between number and string.

## Change fields type of inserted file
`PATCH CLUSTER_IP:5003/fieldtypes/<filename>`

The request uses filename as id in argument and fields in body, fields are an 
array with all fields from file to be changed, using number or string 
descriptor in each Key:Value to describe the new value of altered field of 
file.

```json
{
    "field1": "number",
    "field2": "string"
}
```
