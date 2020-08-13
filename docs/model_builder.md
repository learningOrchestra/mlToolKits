# Model builder microservice
Model Builder microservice provide a REST API to create several model predictions using your own preprocessing code using a defined set of classificators. 

## Create prediction model
`POST CLUSTER_IP:5002/models`

```json
{
    "training_filename": "training filename",
    "test_filename": "test filename",
    "preprocessor_code": "Python3 code to preprocessing, using Pyspark library",
    "classificators_list": "String list of classificators to be used"
}
```
### classificators_list

* "lr": LogisticRegression
* "dt": DecisionTreeClassifier
* "rf": RandomForestClassifier
* "gb": Gradient-boosted tree classifier
* "nb": NaiveBayes

to send a request with LogisticRegression and NaiveBayes classificators:
```json
{
    "training_filename": "training filename",
    "test_filename": "test filename",
    "preprocessor_code": "Python3 code to preprocessing, using Pyspark library",
    "classificators_list": ["lr", "nb"]
}
```

### preprocessor_code environment

The python3 preprocessing code must use the environment instances in bellow:

* training_df (Instanciated): Spark Dataframe instance for trainingfilename
* testing_df  (Instanciated): Spark Dataframe instance for testing filename

The preprocessing code must instanciate the variables in bellow, , all intances must be transformed by pyspark VectorAssembler:

* features_training (Not Instanciated): Spark Dataframe instance for train the model
* features_evaluation (Not Instanciated): Spark Dataframe instance for evaluate trained model accuracy
* features_testing (Not Instanciated): Spark Dataframe instance for test the model

Case you don't want evaluate the model prediction, define features_evaluation as None.

#### Handy methods

```python
self.fields_from_dataframe(self, dataframe, is_string)
```
This method return string or number fields as string list from a dataframe

* dataframe: dataframe instance
* is_string: Boolean parameter, if True, the method return the string dataframe fields, otherwise, return the numbers dataframe fields.

#### preprocessor_code example

``` python
from pyspark.ml import Pipeline
from pyspark.sql.functions import (
    mean, col, split,
    regexp_extract, when, lit)

from pyspark.ml.feature import (
    VectorAssembler,
    StringIndexer
)

TRAINING_DF_INDEX = 0
TESTING_DF_INDEX = 1

training_df = training_df.withColumnRenamed('Survived', 'label')
testing_df = testing_df.withColumn('label', lit(0))
datasets_list = [training_df, testing_df]

for index, dataset in enumerate(datasets_list):
    dataset = dataset.withColumn(
        "Initial",
        regexp_extract(col("Name"), "([A-Za-z]+)\.", 1))
    datasets_list[index] = dataset


misspelled_initials = ['Mlle', 'Mme', 'Ms', 'Dr', 'Major', 'Lady', 'Countess',
                       'Jonkheer', 'Col', 'Rev', 'Capt', 'Sir', 'Don']
correct_initials = ['Miss', 'Miss', 'Miss', 'Mr', 'Mr', 'Mrs', 'Mrs',
                    'Other', 'Other', 'Other', 'Mr', 'Mr', 'Mr']
for index, dataset in enumerate(datasets_list):
    dataset = dataset.replace(misspelled_initials, correct_initials)
    datasets_list[index] = dataset


initials_age = {"Miss": 22,
                "Other": 46,
                "Master": 5,
                "Mr": 33,
                "Mrs": 36}
for index, dataset in enumerate(datasets_list):
    for initial, initial_age in initials_age.items():
        dataset = dataset.withColumn(
            "Age",
            when((dataset["Initial"] == initial) &
                 (dataset["Age"].isNull()), initial_age).otherwise(
                    dataset["Age"]))
        datasets_list[index] = dataset


for index, dataset in enumerate(datasets_list):
    dataset = dataset.na.fill({"Embarked": 'S'})
    datasets_list[index] = dataset


for index, dataset in enumerate(datasets_list):
    dataset = dataset.withColumn("Family_Size", col('SibSp')+col('Parch'))
    dataset = dataset.withColumn('Alone', lit(0))
    dataset = dataset.withColumn(
        "Alone",
        when(dataset["Family_Size"] == 0, 1).otherwise(dataset["Alone"]))
    datasets_list[index] = dataset


text_fields = ["Sex", "Embarked", "Initial"]
for column in text_fields:
    for index, dataset in enumerate(datasets_list):
        dataset = StringIndexer(
            inputCol=column, outputCol=column+"_index").\
                fit(dataset).\
                transform(dataset)
        datasets_list[index] = dataset


non_required_columns = ["Name", "Ticket", "Cabin",
                        "Embarked", "Sex", "Initial"]
for index, dataset in enumerate(datasets_list):
    dataset = dataset.drop(*non_required_columns)
    datasets_list[index] = dataset


training_df = datasets_list[TRAINING_DF_INDEX]
testing_df = datasets_list[TESTING_DF_INDEX]

assembler = VectorAssembler(
    inputCols=training_df.columns[1:],
    outputCol="features")
assembler.setHandleInvalid('skip')

features_training = assembler.transform(training_df)
(features_training, features_evaluation) =\
    features_training.randomSplit([0.1, 0.9], seed=11)
features_testing = assembler.transform(testing_df)
```