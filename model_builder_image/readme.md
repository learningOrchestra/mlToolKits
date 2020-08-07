# modelbuilder microservice
modelbuilder microservice provide an api to create preprocess models from training and tests files inserted in database service, generating a preprocessed files, sending the resulted files to modelbuilder microservice.

## POST IP:5002/models
```
{
    "training_filename": "training filename",
    "test_filename": "test filename",
    "preprocessor_code": "Python3 code to preprocessing, using Pyspark library
    "classificators_list": String list of classificators to be used
}
```
### Classificators

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
### Handy methods

`self.fields_from_dataframe(self, dataframe, is_string)`

* dataframe: dataframe instance
* is_string: Boolean parameter, if True, the method return the string dataframe fields, otherwise, return the numbers dataframe fields.

### preprocessing_code environment

The python3 preprocessing code must use the environment instances in bellow:

* training_df (Instanciated): Spark Dataframe instance for trainingfilename
* testing_df  (Instanciated): Spark Dataframe instance for testing filename

The preprocessing code must instanciate the variables in bellow, , all intances must be transformed by pyspark VectorAssembler:

* features_training (Not Instanciated): Spark Dataframe instance for train the model
* features_evaluation (Not Instanciated): Spark Dataframe instance for evaluate trained model accuracy
* features_testing (Not Instanciated): Spark Dataframe instance for test the model

Case you don't want evaluate the model prediction, define features_evaluation as None.

#### Example

    from pyspark.ml import Pipeline
    from pyspark.sql import functions as sf
    from pyspark.sql.functions import mean,col,split, col, regexp_extract, when, lit
    from pyspark.ml.feature import VectorAssembler, StringIndexer, QuantileDiscretizer

    training_df = training_df.withColumn("Initial",regexp_extract(col("Name"),"([A-Za-z]+)\.",1))
    training_df = training_df.withColumnRenamed('Survived', 'label')
    training_df = training_df.replace(['Mlle','Mme', 'Ms', 'Dr','Major','Lady','Countess','Jonkheer','Col','Rev','Capt','Sir','Don'],
                ['Miss','Miss','Miss','Mr','Mr',  'Mrs',  'Mrs',  'Other',  'Other','Other','Mr','Mr','Mr'])

    testing_df = testing_df.withColumn("Initial",regexp_extract(col("Name"),"([A-Za-z]+)\.",1))
    testing_df = testing_df.replace(['Mlle','Mme', 'Ms', 'Dr','Major','Lady','Countess','Jonkheer','Col','Rev','Capt','Sir','Don'],
                ['Miss','Miss','Miss','Mr','Mr',  'Mrs',  'Mrs',  'Other',  'Other','Other','Mr','Mr','Mr'])

    testing_df = testing_df.withColumn('label', sf.lit(0))

    training_df = training_df.withColumn("Age",when((training_df["Initial"] == "Miss") & (training_df["Age"].isNull()), 22).otherwise(training_df["Age"]))
    training_df = training_df.withColumn("Age",when((training_df["Initial"] == "Other") & (training_df["Age"].isNull()), 46).otherwise(training_df["Age"]))
    training_df = training_df.withColumn("Age",when((training_df["Initial"] == "Master") & (training_df["Age"].isNull()), 5).otherwise(training_df["Age"]))
    training_df = training_df.withColumn("Age",when((training_df["Initial"] == "Mr") & (training_df["Age"].isNull()), 33).otherwise(training_df["Age"]))
    training_df = training_df.withColumn("Age",when((training_df["Initial"] == "Mrs") & (training_df["Age"].isNull()), 36).otherwise(training_df["Age"]))

    testing_df = testing_df.withColumn("Age",when((testing_df["Initial"] == "Miss") & (testing_df["Age"].isNull()), 22).otherwise(testing_df["Age"]))
    testing_df = testing_df.withColumn("Age",when((testing_df["Initial"] == "Other") & (testing_df["Age"].isNull()), 46).otherwise(testing_df["Age"]))
    testing_df = testing_df.withColumn("Age",when((testing_df["Initial"] == "Master") & (testing_df["Age"].isNull()), 5).otherwise(testing_df["Age"]))
    testing_df = testing_df.withColumn("Age",when((testing_df["Initial"] == "Mr") & (testing_df["Age"].isNull()), 33).otherwise(testing_df["Age"]))
    testing_df = testing_df.withColumn("Age",when((testing_df["Initial"] == "Mrs") & (testing_df["Age"].isNull()), 36).otherwise(testing_df["Age"]))


    training_df = training_df.na.fill({"Embarked" : 'S'})
    training_df = training_df.drop("Cabin")
    training_df = training_df.withColumn("Family_Size",col('SibSp')+col('Parch'))
    training_df = training_df.withColumn('Alone',lit(0))
    training_df = training_df.withColumn("Alone",when(training_df["Family_Size"] == 0, 1).otherwise(training_df["Alone"]))

    testing_df = testing_df.na.fill({"Embarked" : 'S'})
    testing_df = testing_df.drop("Cabin")
    testing_df = testing_df.withColumn("Family_Size",col('SibSp')+col('Parch'))
    testing_df = testing_df.withColumn('Alone',lit(0))
    testing_df = testing_df.withColumn("Alone",when(testing_df["Family_Size"] == 0, 1).otherwise(testing_df["Alone"]))

    for column in ["Sex","Embarked","Initial"]:
        training_df = StringIndexer(inputCol=column, outputCol=column+"_index").fit(training_df).transform(training_df)
        testing_df = StringIndexer(inputCol=column, outputCol=column+"_index").fit(testing_df).transform(testing_df)


    training_df = training_df.drop("Name","Ticket","Cabin","Embarked","Sex","Initial")

    testing_df = testing_df.drop("Name","Ticket","Cabin","Embarked","Sex","Initial")

    assembler = VectorAssembler(inputCols=training_df.columns[1:],outputCol="features")
    assembler.setHandleInvalid('skip')

    features_training = assembler.transform(training_df)
    (features_training, features_evaluation) = features_training.randomSplit([0.1, 0.9], seed=11)
    # features_evaluation = None
    features_testing = assembler.transform(testing_df)
 