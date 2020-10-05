<p align="center">
    <img src="./learning-orchestra.png">
    <img src="https://img.shields.io/badge/build-passing-brightgreen?style=flat-square" href="https://shields.io/" alt="build-passing">
    <img src="https://img.shields.io/github/v/tag/riibeirogabriel/learningOrchestra?style=flat-square" href="https://github.com/riibeirogabriel/learningOrchestra/tags" alt="tag">
    <img src="https://img.shields.io/github/last-commit/riibeirogabriel/learningOrchestra?style=flat-square" href="https://github.com/riibeirogabriel/learningOrchestra/tags" alt="last-commit">
    <img src="https://img.shields.io/badge/all_contributors-6-orange.svg?style=flat-square" href="#contributors-" alt="All Contributors">
</p>

# learningOrchestra

**learningOrchestra** facilitates and streamlines iterative processes in a Data Science project pipeline like:

* Data Gathering
* Data Cleaning
* Model Building
* Validating the Model
* Presenting the Results

With learningOrchestra, you can:

* load a dataset from an URL (in CSV format).
* accomplish several pre-processing tasks with datasets.
* create highly customised model predictions against a specific dataset by providing their own pre-processing code.
* build prediction models with different classifiers simultaneously using a spark cluster transparently.

And so much more! Check the [usage section](#usage) for more.

# Installation

## Requirements

* Linux hosts
* [Docker Engine](https://docs.docker.com/engine/install/) must be installed in all instances of your cluster
* Cluster configured in swarm mode, check [creating a swarm](https://docs.docker.com/engine/swarm/swarm-tutorial/create-swarm/)
* [Docker Compose](https://docs.docker.com/compose/install/) must be installed in the manager instance of your cluster

*Ensure that your cluster environment does not block any traffic such as firewall rules in your network or in your hosts.*

*If in case, you have firewalls or other traffic-blockers, add learningOrchestra as an exception.*

Ex: In Google Cloud Platform each of the VMs must allow both http and https traffic.

## Deployment

In the manager Docker swarm machine, clone the repo using:

```
git clone https://github.com/learningOrchestra/learningOrchestra.git
```

Navigate into the `learningOrchestra` directory and run:

```
cd learningOrchestra
sudo ./run.sh
```

That's it! learningOrchestra has been deployed in your swarm cluster!

## Cluster State

`CLUSTER_IP:80` - To visualize cluster state (deployed microservices and cluster's machines).
`CLUSTER_IP:8080` - To visualize spark cluster state.

*\** `CLUSTER_IP` *is the external IP of a machine in your cluster.*

# Usage

learningOrchestra can be used with the [Microservices REST API](#microservices-rest-apis) or with the `learning-orchestra-client` [Python package](https://pypi.org/project/learning-orchestra-client/).

## Microservices REST APIs

[Database API](https://learningorchestra.github.io/learningOrchestra-docs/database-api)- Download and handle datasets in a database.

[Projection API](https://learningorchestra.github.io/learningOrchestra-docs/projection-api)- Make projections of stored datasets using Spark cluster.

[Data type API](https://learningorchestra.github.io/learningOrchestra-docs/datatype-api)- Change dataset fields type between number and text.

[Histogram API](https://learningorchestra.github.io/learningOrchestra-docs/histogram-api)- Make histograms of stored datasets.

[t-SNE API](https://learningorchestra.github.io/learningOrchestra-docs/t-sne-api)- Make a t-SNE image plot of stored datasets.

[PCA API](https://learningorchestra.github.io/learningOrchestra-docs/pca-api)- Make a PCA image plot of stored datasets.

[Model builder API](https://learningorchestra.github.io/learningOrchestra-docs/modelbuilder-api)- Create a prediction model from pre-processed datasets using Spark cluster.

### Spark Microservices

The Projection, t-SNE, PCA and Model builder microservices uses the Spark microservice to work.

By default, this microservice has only one instance. In case your data processing requires more computing power, you can scale this microservice.

To do this, with learningOrchestra already deployed, run the following in the manager machine of your Docker swarm cluster:

`docker service scale microservice_sparkworker=NUMBER_OF_INSTANCES`

*\** `NUMBER_OF_INSTANCES` *is the number of Spark microservice instances which you require. Choose it according to your cluster resources and your resource requirements.*

## Database GUI

NoSQLBooster- MongoDB GUI performs several database tasks such as file visualization, queries, projections and file extraction to CSV and JSON formats. 
It can be util to accomplish some these tasks with your processed dataset or get your prediction results.

Read the [Database API docs](https://learningorchestra.github.io/learningOrchestra-docs/database_api) for more info on configuring this tool.

See the [full docs](https://learningorchestra.github.io/learningOrchestra-docs/usage/) for detailed usage instructions.

## Contributors ✨

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
