# Install

## Requirements

* Linux hosts;
* [Docker Engine](https://docs.docker.com/engine/install/) installed in all instances of your cluster;
* Cluster configured in swarm mode, more details in [swarm documentation](https://docs.docker.com/engine/swarm/swarm-tutorial/create-swarm/);
* [Docker Compose](https://docs.docker.com/compose/install/) installed in manager instance of your cluster; and
* Ensure which your cluster environment has no network traffic block, as firewalls rules in your network or owner firewall in linux hosts, case has firewalls or other blockers, insert learningOrchestra in blocked exceptions, as example, in Google Cloud Platform the VMs must be with allow_http and allow_https firewall rules allowed in each VM configuration.

## Deploy

In your manager docker swarm machine, ensure that you are located in the project root `./learningOrchestra` and run the command below in `sudo` mode to deploy the learningOrchestra:
```
sudo ./run.sh
```
If everything goes according to plan, learningOrchestra has been deployed in your swarm cluster. Congrulations! 🥳 👏

## learningOrchestra Cluster State
There are two web pages for cluster state visualization:

* Visualize cluster state (deployed microservices and cluster's machines) - `CLUSTER_IP:80`
* Visualize spark cluster state - `CLUSTER_IP:8080`.

The `CLUSTER_IP` is an external IP of a machine in your cluster.

