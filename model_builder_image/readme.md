# modelbuilder service
modelbuilder service provide an api to create models from training and tests files inserted in database service, generating a prediction, using testing file to validate the prediction.

## POST IP:5002/models
```
{
    "training_filename": "training filename",
    "test_filename": "test filename",
    "label": "label name on fields of training_filename"
}
```

 