# modelpreprocessor microservice
modelpreprocessor microservice provide an api to create preprocess models from training and tests files inserted in database service, generating a preprocessed files, sending the resulted files to modelbuilder microservice.

## POST IP:5002/preprocessors
```
{
    "training_filename": "training filename",
    "test_filename": "test filename",
    "preprocessor_code": "Python code to preprocessing, using Pyspark library
    "model_classificator": String list of classificators to be used
}
```
## Classificators

* "lr": LogisticRegression
* "dt": DecisionTreeClassifier
* "rf": RandomForestClassifier
* "gb": Gradient-boosted tree classifier
* "nb": NaiveBayes
* "svm": Support Vector Machine

to send a request with LogisticRegression and NaiveBayes classificators:
```
{
    ...
    "model_classificator": ["lr", "nb"]
}
```

## Preprocessor code environment

The python preprocessing code must use the environment instances in bellow:

* training_df (Instanciated): Spark Dataframe instance for training filename
* testing_df  (Instanciated): Spark Dataframe instance for testing filename
* assembler (Instanciated): Clear Spark VectorAssembler instance for features join , need set inputCols and setHandleInvalid parameters

### Handy methods

`self.fields_from_dataframe(self, dataframe, is_string)`

* dataframe: dataframe instance
* is_string: Boolean parameter, if True, the method return the string dataframe fields, otherwise, return the numbers dataframe fields.

 