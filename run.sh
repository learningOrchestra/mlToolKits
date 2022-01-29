#!/bin/bash

echo "learningOrchestra: a distributed machine learning processing tool"
echo "--------------------------------------------------------------------"
echo "Building the learningOrchestra microservice images..."
echo "--------------------------------------------------------------------"

docker build --tag spark_task microservices/spark_task_image
docker push learningorchestra/spark_task

docker-compose build


echo "--------------------------------------------------------------------"
echo "Pushing the microservice images in  repository..."
echo "--------------------------------------------------------------------"



database_api_repository=learningorchestra/database_api


echo "--------------------------------------------------------------------"
echo "Pushing databaseApi microservice image..."
echo "--------------------------------------------------------------------"
docker push $database_api_repository


spark_repository=learningorchestra/spark

echo "--------------------------------------------------------------------"
echo "Pushing spark image..."
echo "--------------------------------------------------------------------"
docker push $spark_repository


projection_repository=learningorchestra/projection

echo "--------------------------------------------------------------------"
echo "Pushing projection microservice image..."
echo "--------------------------------------------------------------------"
docker push $projection_repository


builder_repository=learningorchestra/builder

echo "--------------------------------------------------------------------"
echo "Pushing builder microservice image..."
echo "--------------------------------------------------------------------"
docker push $builder_repository


data_type_handler_repository=learningorchestra/data_type_handler

echo "--------------------------------------------------------------------"
echo "Pushing dataTypeHandler microservice image..."
echo "--------------------------------------------------------------------"
docker push $data_type_handler_repository


histogram_repository=learningorchestra/histogram

echo "--------------------------------------------------------------------"
echo "Pushing histogram microservice image..."
echo "--------------------------------------------------------------------"
docker push $histogram_repository


model_repository=learningorchestra/model

echo "--------------------------------------------------------------------"
echo "Pushing model microservice image..."
echo "--------------------------------------------------------------------"
docker push $model_repository


binary_executor_repository=learningorchestra/binary_executor

echo "--------------------------------------------------------------------"
echo "Pushing binaryExecutor microservice image..."
echo "--------------------------------------------------------------------"
docker push $binary_executor_repository


database_executor_repository=learningorchestra/database_executor

echo "--------------------------------------------------------------------"
echo "Pushing databaseExecutor microservice image..."
echo "--------------------------------------------------------------------"
docker push $database_executor_repository


code_executor_repository=learningorchestra/code_executor

echo "--------------------------------------------------------------------"
echo "Pushing codeExecutor microservice image..."
echo "--------------------------------------------------------------------"
docker push $code_executor_repository


gatewayapi_repository=learningorchestra/gatewayapi

echo "--------------------------------------------------------------------"
echo "Pushing gatewayapi microservice image..."
echo "--------------------------------------------------------------------"
docker push $gatewayapi_repository


echo "--------------------------------------------------------------------"
echo "End."
echo "--------------------------------------------------------------------"
