#!/bin/bash

if [ "$SPARK_ROLE" = "master" ]; then
  $SPARK_HOME/bin/spark-class org.apache.spark.deploy.master.Master
fi
if [ "$SPARK_ROLE" = "slave" ]; then
  $SPARK_HOME/bin/spark-class org.apache.spark.deploy.worker.Worker  \
  spark://$SPARK_MASTER:$SPARK_MASTER_PORT -p $SPARK_WORKER_PORT

  $SPARK_HOME/bin/spark-shell --driver-memory 2G 
fi