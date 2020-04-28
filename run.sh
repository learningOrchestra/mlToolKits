#!/bin/bash

echo "learningOrschestra: a machine learning resource orchestrator"
echo "Buiding own service images..."
docker-compose build 

echo "Adding the image service in docker daemon security exception..."
echo '{
  "insecure-registries" : ["127.0.0.1:5050"]
}
' > /etc/docker/daemon.json


echo "Restarting docker service..."
service docker restart

echo "Deploying learningOrchestra in swarm..."
docker stack deploy --compose-file=docker-compose.yml service

echo "Pushing the own service images in local repository..."
docker push 127.0.0.1:5050/database_api:database_api

echo "Done!"