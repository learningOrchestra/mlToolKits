# learningOrchestra: a distributed machine learning processing tool 

[![status](https://img.shields.io/badge/status-building-yellow.svg)](https://shields.io/)
[![tag](https://img.shields.io/github/v/tag/riibeirogabriel/learningOrchestra)](https://github.com/riibeirogabriel/learningOrchestra/tags)
[![last commit](https://img.shields.io/github/last-commit/riibeirogabriel/learningOrchestra)](https://github.com/riibeirogabriel/learningOrchestra/tags)

## What is learningOrchestra?

The learningOrchestra is a software for distributed machine learning processing using microservices in a cluster, is possible load a csv file from a URL using the database api microservice, this csv file is converted to json file to be stored in MongoDB, also is possible make preprocessing tasks using microservices as projection and data type handler.

The main feature of learningOrchestra is make prediction models with different classificators simultaneously using stored and preprocessed datasets with model builder microservice, this microservice use a spark cluster to make prediction models using distributed processing. You can compare the differents classificators result as time to fit and prediction accuracy, the fact of the user usage your own preprocessing code allow the creation of highly customized model predictons to a specific dataset, increasing the accuracy and results, the sky is the limit! :rocket: :rocket:

To turn the learningOrchestra use more easy, there is the learning_orchestra_client python package, this package provide to an user all learningOrchestra functionalities in coding way, to improve your user experience you can export and analyse the results using a GUI of MongoDB as [NoSQLBooster](https://nosqlbooster.com), also there is an [example of usage of learningOrchestra](https://riibeirogabriel.github.io/learningOrchestra/learning_orchestra_client_package/#learning_orchestra_client-usage-example) with the [titanic challenge dataset](https://www.kaggle.com/c/titanic), each microservice and python package have the own documentation with examples of use, more details of how install and how use in [learningOrchestra documentation](https://riibeirogabriel.github.io/learningOrchestra).
