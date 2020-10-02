<p align="center">
    <img src="./learning-orchestra.png">
    <img src="https://img.shields.io/badge/build-passing-brightgreen" href="https://shields.io/" alt="build-passing">
    <img src="https://img.shields.io/github/v/tag/riibeirogabriel/learningOrchestra" href="https://github.com/riibeirogabriel/learningOrchestra/tags" alt="tag">
    <img src="https://img.shields.io/github/last-commit/riibeirogabriel/learningOrchestra" href="https://github.com/riibeirogabriel/learningOrchestra/tags" alt="last-commit">
</p>

# learningOrchestra

**learningOrchestra** facilitates and streamlines iterative processes in a Data Science project pipeline like:

* Data Gathering
* Data Cleaning
* Model Building
* Validating the Model
* Presenting the Results

## Architecture
                                                                    
The architecture of learningOrchestra is a collection of microservices deployed in a cluster.

A dataset (in CSV format) can be loaded from an URL using the [Database API](https://riibeirogabriel.github.io/learningOrchestra/database_api) microservice, which converts the dataset to JSON and later stores it in MongoDB.

It is also possible to perform several preprocessing and analytical tasks using learningOrchestra's [collection of microservices](https://riibeirogabriel.github.io/learningOrchestra/usage).

With learningOrchestra, you can build prediction models with different classifiers simultaneously using stored and preprocessed datasets with the *Model Builder* microservice. This microservice uses a [Spark](https://spark.apache.org/) cluster to make prediction models using distributed processing. You can compare the different classification results over time to fit and increase prediction accuracy.

By providing their own preprocessing code, users can create highly customized model predictions against a specific dataset, increasing model prediction accuracy. With that in mind, the possibilities are endless! 🚀

## Getting Started

To make using learningOrchestra more accessible, we provide the `learning_orchestra_client` Python package. This package provides developers with all of learningOrchestra's functionalities in a Python API.

To improve user experience, a user can export and analyse the results using a MongoDB GUI, such as [NoSQLBooster](https://nosqlbooster.com).

We also built a [demo](https://pypi.org/project/learning-orchestra-client/) of learningOrchestra (in *learning_orchestra_client usage example* section) with the [Titanic challenge dataset](https://www.kaggle.com/c/titanic).

The learningOrchestra [documentation](https://riibeirogabriel.github.io/learningOrchestra) has a more detailed guide on how to install and use it. We also provide documentation and examples for each microservice and Python package.
