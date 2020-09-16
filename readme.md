# learningOrchestra: a distributed machine learning processing tool 

[![status](https://img.shields.io/badge/status-building-yellow.svg)](https://shields.io/)
[![tag](https://img.shields.io/github/v/tag/riibeirogabriel/learningOrchestra)](https://github.com/riibeirogabriel/learningOrchestra/tags)
[![last commit](https://img.shields.io/github/last-commit/riibeirogabriel/learningOrchestra)](https://github.com/riibeirogabriel/learningOrchestra/tags)

## What is learningOrchestra?

The goal of this work is to develop a tool, named learningOrchestra, to reduce
a bit more the existing gap in facilitate and streamline the data scientist 
iterative process composed of gather data, clean/prepare those data, 
build models, validate their predictions and deploy the results.
The learningOrchestra use microservices in a cluster, is possible load a 
dataset in csv format from an URL using the 
[database api](https://riibeirogabriel.github.io/learningOrchestra/database_api) 
microservice, this csv file is converted to json file to be stored in MongoDB, 
also is possible perform several preprocessing and analytical tasks using 
[this microservices](https://riibeirogabriel.github.io/learningOrchestra/usage).

The main feature of learningOrchestra is make prediction models with different 
classificators simultaneously using stored and preprocessed datasets with 
model builder microservice, this microservice use a spark cluster to make 
prediction models using distributed processing. You can compare the different 
classificators result as time to fit and prediction accuracy, the fact of the 
user usage your own preprocessing code allow the creation of highly customized 
model predictions to a specific dataset, increasing the accuracy and results, 
the sky is the limit! 🚀🚀

To turn the learningOrchestra use more easy, there is the 
learning_orchestra_client python package, this package provide to user all 
learningOrchestra functionalities in coding way, to improve your user 
experience you can export and analyse the results using a GUI of MongoDB as 
[NoSQLBooster](https://nosqlbooster.com), also there is an 
[example of usage of learningOrchestra](https://riibeirogabriel.github.io/learningOrchestra/learning_orchestra_client_package/#learning_orchestra_client-usage-example) 
with the [titanic challenge dataset](https://www.kaggle.com/c/titanic), each 
microservice and python package has the own documentation with examples of 
use, more details of how install and how use in 
[learningOrchestra documentation](https://riibeirogabriel.github.io/learningOrchestra).

