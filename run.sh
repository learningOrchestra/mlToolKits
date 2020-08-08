#!/bin/bash

echo "learningOrschestra: a distributed machine learning resource tool"
echo "--------------------------------------------------------------------"
echo "Buiding the learningOrschestra microservice images..."
echo "--------------------------------------------------------------------"

docker build --tag spark_task ./spark_task_image
docker push 127.0.0.1:5050/spark_task

docker-compose build

echo "--------------------------------------------------------------------"
echo "Adding the image microservice in docker daemon security exception..."
echo "--------------------------------------------------------------------"

echo '{
  "insecure-registries" : ["myregistry:5050"]
}
' > /etc/docker/daemon.json

echo "--------------------------------------------------------------------"
echo "Restarting docker service..."
echo "--------------------------------------------------------------------"

service docker restart

echo "--------------------------------------------------------------------"
echo "Deploying learningOrchestra in swarm cluster..."
echo "--------------------------------------------------------------------"

docker stack deploy --compose-file=docker-compose.yml microservice

echo "--------------------------------------------------------------------"
echo "Pushing the microservice images in local repository..."
echo "--------------------------------------------------------------------"

sleep 30


database_api_repository=127.0.0.1:5050/database_api


echo "--------------------------------------------------------------------"
echo "Pushing databaseapi microservice image..."
echo "--------------------------------------------------------------------"
docker push $database_api_repository


spark_repository=127.0.0.1:5050/spark

echo "--------------------------------------------------------------------"
echo "Pushing spark microservice image..."
echo "--------------------------------------------------------------------"
docker push $spark_repository


projection_repository=127.0.0.1:5050/projection

echo "--------------------------------------------------------------------"
echo "Pushing projection microservice image..."
echo "--------------------------------------------------------------------"
docker push $projection_repository


model_builder_repository=127.0.0.1:5050/model_builder

echo "--------------------------------------------------------------------"
echo "Pushing modelbuilder microservice image..."
echo "--------------------------------------------------------------------"
docker push $model_builder_repository


data_type_handler_repository=127.0.0.1:5050/data_type_handler

echo "--------------------------------------------------------------------"
echo "Pushing datatypehandler microservice image..."
echo "--------------------------------------------------------------------"
docker push $data_type_handler_repository

echo "--------------------------------------------------------------------"
echo "End."
echo "--------------------------------------------------------------------"
