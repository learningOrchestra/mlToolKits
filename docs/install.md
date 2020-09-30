# Install

## Requirements

* Linux hosts;
* [Docker Engine](https://docs.docker.com/engine/install/) installed in all 
instances of your cluster;
* cluster configured in swarm mode, more details in 
[swarm documentation](https://docs.docker.com/engine/swarm/swarm-tutorial/create-swarm/);
* [Docker Compose](https://docs.docker.com/compose/install/) installed in 
manager instance of your cluster; and
* Ensure which your cluster environment has no network traffic block, as 
firewalls rules in your network or owner firewall in linux hosts, case has 
firewalls or other blockers, insert learningOrchestra in blocked exceptions, as
 example, in Google Cloud Platform the VMs must be with allow_http and 
 allow_https firewall rules allowed in each VM configuration.

## Deploy

Ensure which your location path is in project root (./learningOrchestra), in 
sequence, run the command bellow in manager instance of your swarm cluster to 
deploy the learningOrchestra:
```
sudo ./run.sh
```
If all things happen good, the learningOrchestra has been deployed in your 
swarm cluster, congrulations! 🥳 👏

## learningOrchestra cluster state
There are two web pages for cluster state visualization:

* Visualize cluster state (deployed microservices and cluster's machines) - 
CLUSTER_IP:80; and
* Visualize spark cluster state - CLUSTER_IP:8080.

The CLUSTER_IP is an external ip of some machine of your cluster.

