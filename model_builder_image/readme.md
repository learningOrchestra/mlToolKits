# modelbuilder microservice
modelbuilder microservice provide an api to create preprocess models from training and tests files inserted in database service, generating a preprocessed files, sending the resulted files to modelbuilder microservice.

## POST IP:5002/models
```
{
    "training_filename": "training filename",
    "test_filename": "test filename",
    "preprocessor_code": "Python code to preprocessing, using Pyspark library
    "classificators_list": String list of classificators to be used
}
```
## Classificators

* "lr": LogisticRegression
* "dt": DecisionTreeClassifier
* "rf": RandomForestClassifier
* "gb": Gradient-boosted tree classifier
* "nb": NaiveBayes
* "svc": Support Vector Machine

to send a request with LogisticRegression and NaiveBayes classificators:
```
{
    ...
    "classificators_list": ["lr", "nb"]
}
```

## modelbuilder code environment

The python preprocessing code must use the environment instances in bellow:

* training_df (Instanciated): Spark Dataframe instance for trainingfilename
* testing_df  (Instanciated): Spark Dataframe instance for testing filename

The preprocessing code must instanciate the variables in bellow, , all intances must be transformed by VectorAssembler:

* features_training (Not Instanciated): Spark Dataframe instance for train the model
* features_evaluation (Not Instanciated): Spark Dataframe instance for evaluate trained model accuracy
* features_testing (Not Instanciated): Spark Dataframe instance for test the model

Case you don't want evaluate the model prediction, define features_evaluation as None.

### Handy methods

`self.fields_from_dataframe(self, dataframe, is_string)`

* dataframe: dataframe instance
* is_string: Boolean parameter, if True, the method return the string dataframe fields, otherwise, return the numbers dataframe fields.

 