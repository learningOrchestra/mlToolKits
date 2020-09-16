# What is? 

## learningOrchestra

The goal of this work is to develop a tool, named Learning Orchestra, to reduce
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
[model builder](https://riibeirogabriel.github.io/learningOrchestra/model_builder) 
microservice, this microservice use a spark cluster to make prediction models 
using distributed processing. You can compare the different classificators 
result as time to fit and prediction accuracy, the fact of the user usage your 
own preprocessing code allow the creation of highly customized model 
predictions to a specific dataset, increasing the accuracy and results, 
the sky is the limit! 🚀🚀

To turn the learningOrchestra use more easy, there is the 
[learning_orchestra_client](https://riibeirogabriel.github.io/learningOrchestra/learning_orchestra_client_package) 
python package, this package provide to an user all learningOrchestra 
functionalities in coding way, to improve your user experience you can export 
and analyse the results using a GUI of MongoDB as 
[NoSQLBooster](https://nosqlbooster.com), also there is an 
[example of usage of learningOrchestra](https://riibeirogabriel.github.io/learningOrchestra/learning_orchestra_client_package/#learning_orchestra_client-usage-example) 
with the [titanic challenge dataset](https://www.kaggle.com/c/titanic), each 
microservice and python package has the own documentation with examples of 
use, more details in below.

## Architecture

![architecture](./architecture.png)

