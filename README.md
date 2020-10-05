**Wondering how to combine your various library and infrastructure needs for your latest data mining project? Just pick the bricks to build your pipeline and learningOrchestra will take care of the rest.**

<p align="center">
    <img src="./learning-orchestra.png">
    <img src="https://img.shields.io/badge/build-passing-brightgreen?style=flat-square" href="https://shields.io/" alt="build-passing">
    <img src="https://img.shields.io/github/v/tag/riibeirogabriel/learningOrchestra?style=flat-square" href="https://github.com/riibeirogabriel/learningOrchestra/tags" alt="tag">
    <img src="https://img.shields.io/github/last-commit/riibeirogabriel/learningOrchestra?style=flat-square" href="https://github.com/riibeirogabriel/learningOrchestra/tags" alt="last-commit">
    <img src="https://img.shields.io/badge/all_contributors-6-orange.svg?style=flat-square" href="#contributors-" alt="All Contributors">
</p>

# learningOrchestra

## Introduction

### Context

Nowadays, **data science relies on a wide range of computer science skills**, from data management to algorithm design, from code optimization to cloud infrastructures. Data scientists are expected to have expertise in these diverse fields, especially when working in small teams or for academia.

This situation can constitute a barrier to the actual extraction of new knowledge from collected data, which is why the last two decades have seen more efforts to facilitate and streamline the development of data mining workflows. The tools created can be sorted into two categories: **high-level** tools facilitate the building of **automatic data processing pipelines** (e.g. :question:) while **low-level** ones support the setup of appropriate physical and virtual infrastructure (e.g. :question:).

However, this landscape is still missing a tool that **encompasses all steps and needs of a typical data science project**. This is where learningOrchestra comes in.

### The learningOrchestra system

learningOrchestra aims to facilitate the development of complex data mining workflows by **seamlessly interfacing different data science tools and services**. From a single interoperable Application Programming Interface (API), users can **design their analytical pipelines and deploy them in an environment with the appropriate capabilities**.

learningOrchestra is designed for data scientists from both engineering and academia backgrounds, so that they can **focus on the discovery of new knowledge** in their data rather than library or maintenance issues.

<!-- TOC depthFrom:2 depthTo:4 withLinks:1 updateOnSave:1 orderedList:0 -->

- [Introduction](#introduction)
	- [Context](#context)
	- [The learningOrchestra system](#the-learningorchestra-system)
- [Quick-start](#quick-start)
- [How do I install learningOrchestra?](#how-do-i-install-learningorchestra)
	- [Setting up your cluster](#setting-up-your-cluster)
	- [Deploy learningOrchestra](#deploy-learningorchestra)
- [How do I use learningOrchestra?](#how-do-i-use-learningorchestra)
	- [Using the microservices REST API](#using-the-microservices-rest-api)
	- [Using the Python package](#using-the-python-package)
	- [Check cluster status](#check-cluster-status)
- [About learningOrchestra](#about-learningorchestra)
	- [Research background](#research-background)
	- [Future steps](#future-steps)
	- [Contributors :sparkles:](#contributors-sparkles)
- [Frequently Asked Questions](#frequently-asked-questions)
	- [On using learningOrchestra](#on-using-learningorchestra)
	- [On the languages and frameworks used by learningOrchestra](#on-the-languages-and-frameworks-used-by-learningorchestra)
	- [On contributing to learningOrchestra](#on-contributing-to-learningorchestra)
- [Requirements](#requirements)
- [Deployment](#deployment)
- [Cluster State](#cluster-state)
- [Microservices REST APIs](#microservices-rest-apis)
	- [Spark Microservices](#spark-microservices)
- [Database GUI](#database-gui)

<!-- /TOC -->

## Quick-start

Installation instructions:
1. learningOrchestra runs on Linux hosts. Install [Docker Engine](https://docs.docker.com/engine/install/) on all instances of your cluster. Configure your cluster in [swarm mode](https://docs.docker.com/engine/swarm/swarm-tutorial/create-swarm/). Install [Docker Compose](https://docs.docker.com/compose/install/) on your manager instance.
2. Clone repo on your manager instance. `https://github.com/learningOrchestra/learningOrchestra.git`
3. `cd learningOrchestra`
4. Deploy with `sudo ./run.sh`

learningOrchestra provides two options to access its features: a microservice REST API and a Python package.

Microservice REST API: We recommand using a GUI REST API caller like [Postman](https://www.postman.com/product/api-client/) or [Insomnia](https://insomnia.rest/). Check the [list of available microservices](https://learningorchestra.github.io/learningOrchestra-docs/usage/#microservices-rest-apis) for requests details.

Python package:
- Python 3 package
- Install with `pip install learning-orchestra-client`
- Start your scripts by import the package and providing the IP address of one of the instances of your cluster:
```
from learning_orchestra_client import *
cluster_ip = "xx.xx.xxx.xxx"
Context(cluster_ip)
```
- Each microservice is wrapped into a class. Check the [package documentation](https://learningorchestra.github.io/learningOrchestra-docs/python-apis/) for a list of available functions and parameters.

## How do I install learningOrchestra?

:bell: This documentation assumes that the users are familiar with a number of advanced computer science concepts. We have tried to link to learning resources to support beginners, as well as introduce some of the concepts in the [FAQ](#frequently-asked-questions). But if something is still not clear, don't hesitate to [ask for help](#on-using-learningOrchestra).

### Setting up your cluster

learningOrchestra operates from a [cluster](#what-is-a-cluster?) of Docker [containers](#what-is-a-container?).

All your hosts must operate under Linux distributions and have [Docker Engine](https://docs.docker.com/engine/install/) installed.

Configure your cluster in [swarm mode](https://docs.docker.com/engine/swarm/swarm-tutorial/create-swarm/). Install [Docker Compose](https://docs.docker.com/compose/install/) on your manager instance.

You are ready to deploy! :tada:

### Deploy learningOrchestra

Clone this repository on your manager instance.
- Using HTTP protocol, `git clone https://github.com/learningOrchestra/learningOrchestra.git`
- Using SSH protocol, `git clone git@github.com:learningOrchestra/learningOrchestra.git`
- Using GitHub CLI, `gh repo clone learningOrchestra/learningOrchestra`

Move to the root of the directory, `cd learningOrchestra`.

Deploy with `sudo ./run.sh`. The deploy process should take a dozen minutes.

##### Interrupt learningOrchestra

Run `docker stack rm microservice`.

## How do I use learningOrchestra?

learningOrchestra is organised into interoperable [microservices](#what-are-microservices?). They offer access to third-party libraries, frameworks and software to **gather data**, **clean data**, **train machine learning models**, **evaluate machine learning models** and **visualize data and results**.

The following microservices are available in the current version:
- Database API- Gather data
- Projection API- Visualize data and results (I'm assuming we're talking about mapping data points into display points?)
- Data type API- Clean data
- Histogram API- Visualize data and results
- t-SNE API- Train machine learning models + Visualize data and results
- PCA API- Train machine learning models + Visualize data and results
- Model builder API- Train machine learning models

learningOrchestra provides two options to access its features: a microservice REST API and a Python package.

### Using the microservices REST API

We recommand using a **GUI REST API** caller like [Postman](https://www.postman.com/product/api-client/) or [Insomnia](https://insomnia.rest/). Of course, regular `curl` commands from the terminal remain a possibility.

The details for each microservice are available in the [documentation](https://learningorchestra.github.io/learningOrchestra-docs/usage/#microservices-rest-apis).

### Using the Python package

**learning-orchestra-client** is a Python 3 package available through the Python Package Index. Install it with `pip install learning-orchestra-client`.

All your scripts must import the package and create a link to the cluster by providing the IP address to an instance of your cluster. Preface your scripts with the following code:
```
from learning_orchestra_client import *
cluster_ip = "xx.xx.xxx.xxx"
Context(cluster_ip)
```

Check the [package documentation](https://learningorchestra.github.io/learningOrchestra-docs/python-apis/) for a list of available functions and parameters, or the [package repository](https://github.com/learningOrchestra/learningOrchestra-python-client) for an example use case.

### Check cluster status

To check the deployed microservices and machines of your cluster, run `CLUSTER_IP:80` where *CLUSTER_IP* is replaced by the external IP of a machine in your cluster.

The same can be done to check Spark cluster state with `CLUSTER_IP:8080`.

## About learningOrchestra

### Research background

### Future steps

### Contributors :sparkles:

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="http://www.linkedin.com/in/riibeirogabriel/"><img src="https://avatars0.githubusercontent.com/u/33736256?v=4" width="100px;" alt=""/><br /><sub><b>Gabriel Ribeiro</b></sub></a><br /><a href="https://github.com/learningOrchestra/learningOrchestra/commits?author=riibeirogabriel" title="Code">💻</a> <a href="#infra-riibeirogabriel" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="#projectManagement-riibeirogabriel" title="Project Management">📆</a> <a href="#maintenance-riibeirogabriel" title="Maintenance">🚧</a></td>
    <td align="center"><a href="http://navendu.me"><img src="https://avatars1.githubusercontent.com/u/49474499?v=4" width="100px;" alt=""/><br /><sub><b>Navendu Pottekkat</b></sub></a><br /><a href="https://github.com/learningOrchestra/learningOrchestra/commits?author=navendu-pottekkat" title="Documentation">📖</a> <a href="#design-navendu-pottekkat" title="Design">🎨</a> <a href="#ideas-navendu-pottekkat" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/hiperbolt"><img src="https://avatars2.githubusercontent.com/u/14186706?v=4" width="100px;" alt=""/><br /><sub><b>hiperbolt</b></sub></a><br /><a href="https://github.com/learningOrchestra/learningOrchestra/commits?author=hiperbolt" title="Code">💻</a> <a href="#ideas-hiperbolt" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="http://www.hpclab.net.br"><img src="https://avatars0.githubusercontent.com/u/1683241?v=4" width="100px;" alt=""/><br /><sub><b>Joubert de Castro Lima</b></sub></a><br /><a href="#ideas-joubertlima" title="Ideas, Planning, & Feedback">🤔</a> <a href="#projectManagement-joubertlima" title="Project Management">📆</a></td>
    <td align="center"><a href="https://github.com/lauromoraes"><img src="https://avatars1.githubusercontent.com/u/312025?v=4" width="100px;" alt=""/><br /><sub><b>Lauro Moraes</b></sub></a><br /><a href="#ideas-lauromoraes" title="Ideas, Planning, & Feedback">🤔</a> <a href="#projectManagement-lauromoraes" title="Project Management">📆</a></td>
    <td align="center"><a href="https://github.com/LaChapeliere"><img src="https://avatars2.githubusercontent.com/u/7062546?v=4" width="100px;" alt=""/><br /><sub><b>LaChapeliere</b></sub></a><br /><a href="https://github.com/learningOrchestra/learningOrchestra/commits?author=LaChapeliere" title="Documentation">📖</a></td>
  </tr>
</table>

<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

## Frequently Asked Questions

###### Where can I find the documentation?

###### What is the website linked to the repo?

###### Who is doing this?

###### Do you get money from learningOrchestra? How do you fund the project?

### On using learningOrchestra

###### I have a question/a feature request/some feedback, how do I contact you?
Please use the [**Issues** page]() of this repo. Check out the [Contributing](##Contributing) section for more details.

###### Can I copy your code for my project?

###### How do I cite learningOrchestra in my paper?

###### Where can I find data?

###### My computer runs on Windows/OSX, can I still use learningOrchestra?

###### I have a single computer, can I still use learningOrchestra?

###### What happens if learningOrchestra is killed while using a microservice?

###### What happens if my instances loose the connection to each other?

###### How do I interrupt learningOrchestra?

### On the languages and frameworks used by learningOrchestra

###### What is a container?

###### What is a cluster?

###### What are microservices?

Microservices - also known as the microservice architecture - is an architectural style that structures an application as a collection of services that are. Highly maintainable and testable. Loosely coupled. Independently deployable. Organized around business capabilities. Owned by small team.
[an overview of microservice architecture](https://medium.com/hashmapinc/the-what-why-and-how-of-a-microservices-architecture-4179579423a9)

###### Method X is very useful and should be included, why is it not there?

### On contributing to learningOrchestra

##### I want to contribute, where do I start?

##### I'm not a developer, can I contribute?
