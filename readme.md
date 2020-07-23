# learningOrchestra: a machine learning resource orchestrator 

[![status](https://img.shields.io/badge/status-building-yellow.svg)](https://shields.io/)
[![tag](https://img.shields.io/github/v/tag/riibeirogabriel/learningOrchestra)](https://github.com/riibeirogabriel/learningOrchestra/tags)
[![last commit](https://img.shields.io/github/last-commit/riibeirogabriel/learningOrchestra)](https://github.com/riibeirogabriel/learningOrchestra/tags)


The learningOrchestra is a tool for distributed machine learning processing.

# Microservices

* visualizer - Visualize cluster state, including machines, up microservices, resources, etc
* images - Private image repository to store images for own projects
* database primary - Main database, used to read and write data
* database secondary - Database used in downtime database_primary , used only to read
* database arbiter - Manage the database replica set, setting database_primary and database_secondary
* [database api](/database_api_image) - Service used to download and handling files in database
* spark master - Manager of spark cluster
* spark worker - Worker of spark cluster
* [projection](/projection_image) - Make projections of stored files in database using spark cluster
* [data type handler](/data_type_handler_image) - Change fields file type between number and text
* [model builder](/model_builder_image) - Create a prediction model from pre-processed files using spark cluster

## Tools and techniques used in this project

* [Docker](https://docs.docker.com/get-started/) - Container 
* [Docker Swarm](https://docs.docker.com/engine/swarm/) - Container Orchestrator 
* [Bitnami MongoDb](https://github.com/bitnami/bitnami-docker-mongodb) - A custom image from MongoDB 
* [GridFS](https://docs.mongodb.com/manual/core/gridfs/) - Mongo specification to work with large size files  ( > 16 MB) 
* [Visualizer](https://hub.docker.com/r/dockersamples/visualizer) - A service to state visualization of cluster 
* [Registry](https://hub.docker.com/_/registry) -  A private image repository service 
* [Mongo Replication](https://docs.mongodb.com/manual/replication/) - Data replication in mongo instances
* [Spark](https://spark.apache.org/) - Large-scale data processing engine

## Documentation

### Requirements

* Linux hosts 
* [Docker Engine](https://docs.docker.com/engine/install/) installed in all instances of your cluster
* [Docker Compose](https://docs.docker.com/compose/install/) installed in manager instance of your cluster
* Ensure wich your cluster environment no has network traffic block, as firewalls rules in your network or owner firewall in linux hosts, case has firewalls or other blockers, insert learningOrchestra in blocked exceptions

### Deploy

Firstly, your cluster must being pre-configured in swarm mode, in your manager instance, insert this command bellow: 
```
sudo docker swarm init --advertise-addr IP_MANAGER
```
Where IP_MANAGER is the manager machine ip on your cluster network. The command result return another command to be insert in all another machines (workers) in your cluster, to be joined in swarm, more details in [swarm documentation](https://docs.docker.com/engine/swarm/swarm-tutorial/create-swarm/).

Ensure wich you location path is in project root (./learningOrchestra), in sequence, run the command bellow in manager instance to build and configure the learningOrchestra in your swarm cluster:
```
chmod 755 run.sh
sudo ./run.sh
```
If all things is happen good, the learningOrchestra is have been deployed in your swarm cluster, congrulations! :clap: :heart_eyes:

### Cluster state
* Visualize cluster state (deployed microservices tasks and cluster's machines) - IP_FROM_CLUSTER:8000
* Visualize Spark Cluster state - IP_FROM_CLUSTER:8080

### Usage
* [learning_orchestra_client](/learning_orchestra_client) - The python package for leanringOrchestra use. 


