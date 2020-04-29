#!/bin/bash

mongo --eval 'rs.initiate({ _id: "replica_set", version: 1, members: [ { _id: 0, host : "database_1" }, { _id: 1, host : "database_2" }, { _id: 2, host : "database_3" } ] })';
