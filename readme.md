# learningOrchestra: a machine learning resource tool 

[![status](https://img.shields.io/badge/status-building-yellow.svg)](https://shields.io/)
[![tag](https://img.shields.io/github/v/tag/riibeirogabriel/learningOrchestra)](https://github.com/riibeirogabriel/learningOrchestra/tags)
[![last commit](https://img.shields.io/github/last-commit/riibeirogabriel/learningOrchestra)](https://github.com/riibeirogabriel/learningOrchestra/tags)


The learningOrchestra is a tool for distributed machine learning processing.

## Documentation

### Requirements

* Linux hosts
* cluster configured in swarm mode, more details in [swarm documentation](https://docs.docker.com/engine/swarm/swarm-tutorial/create-swarm/)
* [Docker Engine](https://docs.docker.com/engine/install/) installed in all instances of your cluster
* [Docker Compose](https://docs.docker.com/compose/install/) installed in manager instance of your cluster
* Ensure wich your cluster environment no has network traffic block, as firewalls rules in your network or owner firewall in linux hosts, case has firewalls or other blockers, insert learningOrchestra in blocked exceptions

### Deploy

Ensure wich you location path is in project root (./learningOrchestra), in sequence, run the command bellow in manager instance to build and configure the learningOrchestra in your cluster:
```
chmod 755 run.sh
sudo ./run.sh
```
If all things is happen good, the learningOrchestra is have been deployed in your swarm cluster, congrulations! :clap: :heart_eyes:

### learningOrchestra state
* Visualize cluster state (deployed microservices tasks and cluster's machines) - IP_FROM_CLUSTER:8000
* Visualize Spark Cluster state - IP_FROM_CLUSTER:8080

### Usage
#### Python package
* [learning_orchestra_client](/learning_orchestra_client) - The python package for learningOrchestra use

#### learningOrchestra microservices REST API request
* [database api](/database_api_image) - Service used to download and handling files in database
* [projection](/projection_image) - Make projections of stored files in database using spark cluster
* [data type handler](/data_type_handler_image) - Change fields file type between number and text
* [model builder](/model_builder_image) - Create a prediction model from pre-processed files using spark cluster

