# learningOrchestra client package

## Installation
Ensure which you have the python 3 installed in your machine and run:
```
pip install learning_orchestra_cliet
```

## Documentation

After downloading the package, import all classes:

``` python
from learning_orchestra_client import *
```

create a Context object passing a ip from your cluster in constructor parameter:

```python
cluster_ip = "34.95.222.197"
Context(cluster_ip)
```

After create a Context object, you will able to usage learningOrchestra, each learningOrchestra funcionalite is contained in your own class, therefore, to use a specific funcionalite, after you instanciate and configure Context class, you need instanciate and call the method class of interest, in below, there are all class and each class methods, also have an example of workflow using this package in a python code.

## DatabaseApi

### read_resume_files

``` python
read_resume_files(pretty_response=True)
```

Read all metadata files in learningOrchestra
* pretty_response: return indented string to visualization (default True, if False, return dict)

### read_file

``` python
read_file(self, filename_key, skip=0, limit=10, query={}, pretty_response=True)
```

* filename_ley : filename of file
* skip: number of rows amount to skip in pagination (default 0)
* limit: number of rows to return in pagination (default 10)(max setted in 20 rows per request)
* query: query to make in mongo (default empty query)
* pretty_response: return indented string to visualization (default True, if False, return dict)

### create_file

``` python
create_file(self, filename, url, pretty_response=True)
```

* filename: filename of file to be created
* url: url to csv file
* pretty_response: return indented string to visualization (default True, if False, return dict)

### delete_file

``` python
delete_file(self, filename, pretty_response=True)
```

* filename: file filename to be deleted
* pretty_response: return indented string to visualization (default True, if False, return dict)

## Projection

### create_projection

``` python
create_projection(self, filename, projection_filename, fields, pretty_response=True)
```

* filename: filename of file to make projection
* projection_filename: filename used to create projection
* field: list with fields to make projection 
* pretty_response: return indented string to visualization (default True, if False, return dict)

## DataTypeHandler

### change_file_type

``` python
change_file_type(self, filename, fields_dict, pretty_response=True)
```

* filename: filename of file
* fields_dict: dictionary with "field": "number" or field: "string" keys  
* pretty_response: return indented string to visualization (default True, if False, return dict)

## ModelBuilder

### create_model

``` python
create_model(self, training_filename, test_filename, preprocessor_code, model_classificator, pretty_response=True)
```

* training_filename: filename to be used in training
* test_filename: filename to be used in test
* preprocessor_code: python3 code for pyspark preprocessing model
* model_classificator: list of initial from classificators to be used in model
* pretty_response: return indented string to visualization (default True, if False, return dict)

#### model_classificator

* "lr": LogisticRegression
* "dt": DecisionTreeClassifier
* "rf": RandomForestClassifier
* "gb": Gradient-boosted tree classifier
* "nb": NaiveBayes

to send a request with LogisticRegression and NaiveBayes classificators:

```python
create_model(training_filename, test_filename, preprocessor_code, ["lr", "nb"])
```

#### preprocessor_code environment

The python 3 preprocessing code must use the environment instances in bellow:

* training_df (Instanciated): Spark Dataframe instance for trainingfilename
* testing_df  (Instanciated): Spark Dataframe instance for testing filename

The preprocessing code must instanciate the variables in bellow, , all intances must be transformed by pyspark VectorAssembler:

* features_training (Not Instanciated): Spark Dataframe instance for train the model
* features_evaluation (Not Instanciated): Spark Dataframe instance for evaluate trained model accuracy
* features_testing (Not Instanciated): Spark Dataframe instance for test the model

Case you don't want evaluate the model prediction, define features_evaluation as None.

##### Handy methods

``` python
self.fields_from_dataframe(self, dataframe, is_string)
```

* dataframe: dataframe instance
* is_string: Boolean parameter, if True, the method return the string dataframe fields, otherwise, return the numbers dataframe fields.

## learning_orchestra_client usage example

In below there is a python script using the package:

``` python
from learning_orchestra_client import *

cluster_ip = "34.95.187.26"

Context(cluster_ip)

database_api = DatabaseApi()

print(database_api.create_file(
    "titanic_training",
    "https://filebin.net/rpfdy8clm5984a4c/titanic_training.csv?t=gcnjz1yo"))
print(database_api.create_file(
    "titanic_testing",
    "https://filebin.net/mguee52ke97k0x9h/titanic_testing.csv?t=ub4nc1rc"))

print(database_api.read_resume_files())

data_type_handler = DataTypeHandler()

print(data_type_handler.change_file_type(
    "titanic_training",
    {
        "Age": "number",
        "Fare": "number",
        "Parch": "number",
        "PassengerId": "number",
        "Pclass": "number",
        "SibSp": "number",
        "Survived": "number"
    }))

print(data_type_handler.change_file_type(
    "titanic_testing",
    {
        "Age": "number",
        "Fare": "number",
        "Parch": "number",
        "PassengerId": "number",
        "Pclass": "number",
        "SibSp": "number"
    }))

preprocessing_code = '''
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
'''

model_builder = Model()

print(model_builder.create_model(
    "titanic_training", "titanic_testing", preprocessing_code,
    ["lr", "dt", "gb", "rf", "nb"]))
```
