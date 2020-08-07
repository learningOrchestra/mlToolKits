# learningOrchestra: a distributed machine learning processing tool 

[![status](https://img.shields.io/badge/status-building-yellow.svg)](https://shields.io/)
[![tag](https://img.shields.io/github/v/tag/riibeirogabriel/learningOrchestra)](https://github.com/riibeirogabriel/learningOrchestra/tags)
[![last commit](https://img.shields.io/github/last-commit/riibeirogabriel/learningOrchestra)](https://github.com/riibeirogabriel/learningOrchestra/tags)

The learningOrchestra is a tool for distributed machine learning processing using microservices deployeds from a cluster, with learningOrchestra, is possible load a csv file from a URL using the [database api](/database_api_image) microservice, this csv file is converted to json file to be stored in mongoDB, with this json file, also is possible make preprocessing tasks using preprocessing microservices as [projection](/projection_image) and [data type handler](/data_type_handler_image).

The main feature of learningOrchestra is make model predictions with different classificators simultaneously using the stored file with [model builder](/model_builder_image) microservice, you can compare the differents classificators result, as time to fit and prediction accuracy. The fact of the user send your own preprocessing code allow the creation of highly customized model predictons to a specific dataset, increasing the accuracy and results, the sky is the limit! :rocket: :rocket:

[Model builder](/model_builder_image) microservice use a spark cluster to make preprocessing and predictions using distributed processing, to make the learningOrchestra use more easy, also there is the  [learning_orchestra_client](/learning_orchestra_client) python package, this package provide to programmer all learningOchestra functionalities in coding way,  you can export and analyse the results using a GUI interface to mongoDB, as [NoSQLBooster](https://nosqlbooster.com), more details in below and in each microservice and package documentation.

## Documentation

### Requirements

* Linux hosts
* [Docker Engine](https://docs.docker.com/engine/install/) installed in all instances of your cluster
* cluster configured in swarm mode, more details in [swarm documentation](https://docs.docker.com/engine/swarm/swarm-tutorial/create-swarm/)
* [Docker Compose](https://docs.docker.com/compose/install/) installed in manager instance of your cluster
* Ensure wich your cluster environment has no network traffic block, as firewalls rules in your network or owner firewall in linux hosts, case has firewalls or other blockers, insert learningOrchestra in blocked exceptions, as example, in Google Cloud Platform the VMs must be with allow_http and allow_https firewall rules allowed in each VM configuration.

### Deploy

Ensure wich you location path is in project root (./learningOrchestra), in sequence, run the command bellow in manager instance to build and configure the learningOrchestra in your cluster:
```
sudo ./run.sh
```
If all things happen good, the learningOrchestra have been deployed in your swarm cluster, congrulations! :clap: :heart_eyes:

### learningOrchestra state
* Visualize cluster state (deployed microservices and cluster's machines) - IP_FROM_CLUSTER:8000
* Visualize spark cluster state - IP_FROM_CLUSTER:8080

### Usage
#### Python package
* [learning_orchestra_client](/learning_orchestra_client) - The python package for learningOrchestra use

#### microservices REST API
* [database api](/database_api_image) - Service used to download and handling files in database
* [projection](/projection_image) - Make projections of stored files in database using spark cluster
* [data type handler](/data_type_handler_image) - Change fields file type between number and text
* [model builder](/model_builder_image) - Create a prediction model from preprocessed files using spark cluster

#### database GUI
* [NoSQLBooster](https://nosqlbooster.com) - MongoDB GUI to make several database tasks, as files visualization, querys, projections and files extraction to formats as csv and json
