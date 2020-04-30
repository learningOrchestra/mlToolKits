#!/usr/bin/env bash

for rs in rs1 rs2 rs3;do
  mongo --host $rs --eval 'db'
  if [ $? -ne 0 ]; then
    exit 1
  fi
done

status=$(mongo --host rs1 --quiet --eval 'rs.status().members.length')
if [ $? -ne 0 ]; then
  mongo --host rs1 --eval 'rs.initiate({ _id: "rs0", version: 1, members: [ { _id: 0, host : "rs1:27017" }, { _id: 1, host : "rs2:27018" }, { _id: 2, host : "rs3:27019" } ] })';
fi