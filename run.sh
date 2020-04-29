#!/bin/bash

echo "learningOrschestra: a machine learning resource orchestrator"
echo "------------------------------------------------"
echo "Buiding own images service..."
echo "------------------------------------------------"

docker-compose build 

echo "------------------------------------------------"
echo "Adding the image service in docker daemon security exception..."
echo "------------------------------------------------"

echo '{
  "insecure-registries" : ["myregistry:5050"]
}
' > /etc/docker/daemon.json

echo "------------------------------------------------"
echo "Restarting docker service..."
echo "------------------------------------------------"

service docker restart

echo "------------------------------------------------"
echo "Deploying learningOrchestra in swarm..."
echo "------------------------------------------------"

docker stack deploy --compose-file=docker-compose.yml service

echo "------------------------------------------------"
echo "Pushing the own service images in local repository..."
echo "------------------------------------------------"

sleep 20
docker push 127.0.0.1:5050/database_api:database_api

echo "------------------------------------------------"
echo "Configuring replica set in database services..."
echo "------------------------------------------------"

sleep 20

for replica_set in database database_replica_1 database_replica_2;
    do  mongo --host $replica_set --eval 'db'
    if [ $? -ne 0 ]; 
        then exit 1
    fi
done

status=$(mongo --host database --quiet --eval 'rs.status().members.length')

if [ $? -ne 0 ]; 
    then mongo --host database --eval 'rs.initiate({ _id: "replica_set", version: 1, '\
                                      'members: [ { _id: 0, host : "database" }, '\
                                      '{ _id: 1, host : "database_replica_2" },'\
                                      ' { _id: 2, host : "database_replica_1" } ] })';
fi

echo "------------------------------------------------"
echo "End."
echo "------------------------------------------------"