# Learning Orquestra: a Machine Learning resource orchestration :whale: (Building) 

The Learning Orchestra is a tool to parallelization of machine learning tasks using microservices.

# Services

![](/readme_content/cluster.png)

## Tools used in this project

* [Docker](https://docs.docker.com/get-started/) - Container 
* [Docker Swarm](https://docs.docker.com/engine/swarm/) - Container Orchestrator 
* [Mongo](https://hub.docker.com/_/mongo) - DataBase 
* [GridFS](https://docs.mongodb.com/manual/core/gridfs/) - Mongo specification to work with large size files  ( > 16 MB) 
* [Visualizer](https://hub.docker.com/r/dockersamples/visualizer) - A service to state visualization of cluster 
* [Registry](https://hub.docker.com/_/registry) -  A private image repository service 

## Documentation

### Requirements

* Linux hosts 
* [Docker Engine](https://docs.docker.com/engine/install/) installed in all instances of your cluster
* [Docker Compose](https://docs.docker.com/compose/install/) installed in manager instance of your cluster

### Deploy

Firstly, your cluster must being pre-configured in swarm mode, in your manager instance, insert this command bellow: 
```
sudo docker swarm init --advertise-addr IP_MANAGER
```
Where IP_MANAGER is the manager machine ip on your cluster network. The command result return another command to be insert in all another machines (workers) in your cluster, to be joined in swarm, more details in [swarm documentation](https://docs.docker.com/engine/swarm/swarm-tutorial/create-swarm/)

Ensure wich you location path is in project root (./learningOrchestra), in sequence, run the command bellow in manager instance to build and configure the learningOrchestra in your swarm cluster:
```
chmod 755 run.sh
sudo ./run.sh
```
If all things is happen good, the learningOrchestra is have been deployed in your swarm cluster, congrulations! :clap: :heart_eyes:

### Use
* Visualize cluster state (deployed services instances and machines) - IP_MANAGER:8080



