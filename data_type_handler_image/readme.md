# data_type_handler service
Service used to change data type from added file between number and string

# POST /type
The request use filename and fields in request body, fields is an array whith all fields from file to be changed, using number or string descriptor in each Key:Value to describe the new value of altered field of filename.
```
{
    "filename": "filename_of_file",
    "fields": {
        "field1": "number"
        "field2": "string"
    }
}
```