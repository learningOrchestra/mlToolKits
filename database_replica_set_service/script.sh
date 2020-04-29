#!/usr/bin/env bash

for database_host in database_1 database_2 database_3;
    do mongo --host $rs --eval 'db'
    if [ $? -ne 0 ];
        then exit 1
    fi
done

status=$(mongo --host database_1 --quiet --eval 'rs.status().members.length')

if [ $? -ne 0 ];
    then mongo --host database_1 --eval 'rs.initiate({ _id: "replica_set", version: 1, members: [ { _id: 0, host : "database_1" }, { _id: 1, host : "database_2" }, { _id: 2, host : "database_3" } ] })';
fi