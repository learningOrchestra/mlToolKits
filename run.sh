#!/bin/bash

echo "learningOrchestra: a distributed machine learning processing tool"
echo "--------------------------------------------------------------------"
echo "Building the learningOrchestra microservice images..."
echo "--------------------------------------------------------------------"

docker build --tag spark_task microservices/spark_task_image
docker push 127.0.0.1:5050/spark_task

docker-compose build

echo "--------------------------------------------------------------------"
echo "Adding the microservice images in docker daemon security exception..."
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
echo "Pushing databaseApi microservice image..."
echo "--------------------------------------------------------------------"
docker push $database_api_repository


spark_repository=127.0.0.1:5050/spark

echo "--------------------------------------------------------------------"
echo "Pushing spark image..."
echo "--------------------------------------------------------------------"
docker push $spark_repository


projection_repository=127.0.0.1:5050/projection

echo "--------------------------------------------------------------------"
echo "Pushing projection microservice image..."
echo "--------------------------------------------------------------------"
docker push $projection_repository


model_builder_repository=127.0.0.1:5050/model_builder

echo "--------------------------------------------------------------------"
echo "Pushing modelBuilder microservice image..."
echo "--------------------------------------------------------------------"
docker push $model_builder_repository


data_type_handler_repository=127.0.0.1:5050/data_type_handler

echo "--------------------------------------------------------------------"
echo "Pushing dataTypeHandler microservice image..."
echo "--------------------------------------------------------------------"
docker push $data_type_handler_repository


histogram_repository=127.0.0.1:5050/histogram

echo "--------------------------------------------------------------------"
echo "Pushing histogram microservice image..."
echo "--------------------------------------------------------------------"
docker push $histogram_repository


tsne_repository=127.0.0.1:5050/tsne

echo "--------------------------------------------------------------------"
echo "Pushing tsne microservice image..."
echo "--------------------------------------------------------------------"
docker push $tsne_repository


pca_repository=127.0.0.1:5050/pca

echo "--------------------------------------------------------------------"
echo "Pushing pca microservice image..."
echo "--------------------------------------------------------------------"
docker push $pca_repository


default_model_repository=127.0.0.1:5050/default_model

echo "--------------------------------------------------------------------"
echo "Pushing defaultModel microservice image..."
echo "--------------------------------------------------------------------"
docker push $default_model_repository


binary_executor_repository=127.0.0.1:5050/binary_executor

echo "--------------------------------------------------------------------"
echo "Pushing binaryExecutor microservice image..."
echo "--------------------------------------------------------------------"
docker push $binary_executor_repository


echo "--------------------------------------------------------------------"
echo "End."
echo "--------------------------------------------------------------------"
