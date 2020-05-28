#!/bin/bash

echo "learningOrschestra: a machine learning resource orchestrator"
echo "--------------------------------------------------------------------"
echo "Buiding own images service..."
echo "--------------------------------------------------------------------"

docker-compose build --no-cache

echo "--------------------------------------------------------------------"
echo "Adding the image service in docker daemon security exception..."
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
echo "Deploying learningOrchestra in swarm..."
echo "--------------------------------------------------------------------"

docker stack deploy --compose-file=docker-compose.yml service

echo "--------------------------------------------------------------------"
echo "Pushing the own service images in local repository..."
echo "--------------------------------------------------------------------"

sleep 30

echo "--------------------------------------------------------------------"
echo "Pushing database_api service image..."
echo "--------------------------------------------------------------------"
docker push 127.0.0.1:5050/database_api:database_api

echo "--------------------------------------------------------------------"
echo "Pushing frontend service image..."
echo "--------------------------------------------------------------------"
docker push 127.0.0.1:5050/frontend:frontend

echo "--------------------------------------------------------------------"
echo "Pushing spark service image..."
echo "--------------------------------------------------------------------"
docker push 127.0.0.1:5050/spark:spark

echo "--------------------------------------------------------------------"
echo "End."
echo "--------------------------------------------------------------------"
