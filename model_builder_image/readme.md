# modelbuilder service
modelbuilder service provide an api to create models from training and tests files inserted in database service, generating a prediction, using testing file to validate the prediction.

## POST IP:5002/models
```
{
    "encoded_assembler": encoded_assembler_object,
    "database_url_training": "database url training",
    "database_url_testing": "database url testing",
    "model_classificator": model classificator list
}
```

 