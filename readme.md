# learningOrchestra: a distributed machine learning processing tool 

[![status](https://img.shields.io/badge/status-building-yellow.svg)](https://shields.io/)
[![tag](https://img.shields.io/github/v/tag/riibeirogabriel/learningOrchestra)](https://github.com/riibeirogabriel/learningOrchestra/tags)
[![last commit](https://img.shields.io/github/last-commit/riibeirogabriel/learningOrchestra)](https://github.com/riibeirogabriel/learningOrchestra/tags)

## What is learningOrchestra?

The learningOrchestra is a software for distributed machine learning processing using microservices in a cluster, is possible load a csv file from a URL using the [database api](/database_api_image) microservice, this csv file is converted to json file to be stored in MongoDB, also is possible make preprocessing tasks using microservices as [projection](/projection_image) and [data type handler](/data_type_handler_image).

The main feature of learningOrchestra is make prediction models with different classificators simultaneously using stored and preprocessed datasets with [model builder](/model_builder_image) microservice, this microservice use a spark cluster to make prediction models using distributed processing. You can compare the differents classificators result as time to fit and prediction accuracy, the fact of the user usage your own preprocessing code allow the creation of highly customized model predictons to a specific dataset, increasing the accuracy and results, the sky is the limit! :rocket: :rocket:

To turn the learningOrchestra use more easy, there is the  [learning_orchestra_client](/learning_orchestra_client) python package, this package provide to an user all learningOrchestra functionalities in coding way, to improve your user experience you can export and analyse the results using a GUI of MongoDB as [NoSQLBooster](https://nosqlbooster.com), also there is an example of usage of learningOrchestra in [learning_orchestra_client docs](/learning_orchestra_client) with the [titanic challenge dataset](https://www.kaggle.com/c/titanic), each microservice and python package have the own documentation with examples of use, more details in below.

## Documentation

### Requirements

* Linux hosts
* [Docker Engine](https://docs.docker.com/engine/install/) installed in all instances of your cluster
* cluster configured in swarm mode, more details in [swarm documentation](https://docs.docker.com/engine/swarm/swarm-tutorial/create-swarm/)
* [Docker Compose](https://docs.docker.com/compose/install/) installed in manager instance of your cluster
* Ensure wich your cluster environment has no network traffic block, as firewalls rules in your network or owner firewall in linux hosts, case has firewalls or other blockers, insert learningOrchestra in blocked exceptions, as example, in Google Cloud Platform the VMs must be with allow_http and allow_https firewall rules allowed in each VM configuration.

### Deploy

Ensure wich you location path is in project root (./learningOrchestra), in sequence, run the command bellow in manager instance of swarm cluster to deploy the learningOrchestra:
```
sudo ./run.sh
```
If all things happen good, the learningOrchestra has been deployed in your swarm cluster, congrulations! :clap: :heart_eyes:

### learningOrchestra state
There are two web pages for cluster state visualization:

* Visualize cluster state (deployed microservices and cluster's machines) - IP_FROM_CLUSTER:8000
* Visualize spark cluster state - IP_FROM_CLUSTER:8080

### Usage
#### Python package
* [learning_orchestra_client docs](/learning_orchestra_client) - The python package for learningOrchestra use

#### microservices REST API
* [database api docs](/database_api_image) - Microservice used to download and handling files in database
* [projection docs ](/projection_image) - Make projections of stored files in database using spark cluster
* [data type handler docs](/data_type_handler_image) - Change fields file type between number and text
* [model builder docs](/model_builder_image) - Create a prediction model from preprocessed files using spark cluster

#### database GUI
* [NoSQLBooster](https://nosqlbooster.com) - MongoDB GUI to make several database tasks, as files visualization, querys, projections and files extraction to formats as csv and json, read the [database api docs](/database_api_image) to learn how configure this tool.
