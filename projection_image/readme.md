# Projection service
Projection service provide an api to make a projection from file inserted in database service, generating a new file and putting in database service

## POST IP:5001/projections/<filename>
```
{
    projection_filename : filename_to_save_projection,
    fields : [list, of, fields, to, be, used, in, projection]
}
```

The files are stored in database service, to read preprocessed files, need use the database_api service 