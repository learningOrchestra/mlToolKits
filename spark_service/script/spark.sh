#!/bin/bash

sed -i '1ispark.driver.memory 1g' $SPARK_HOME/conf/spark-defaults.conf

if [ "$SPARK_ROLE" = "master" ]; then
  $SPARK_HOME/bin/spark-class org.apache.spark.deploy.master.Master
fi
if [ "$SPARK_ROLE" = "slave" ]; then
  $SPARK_HOME/bin/spark-class org.apache.spark.deploy.worker.Worker  \
  spark://$SPARK_MASTER:$SPARK_MASTER_PORT -p $SPARK_WORKER_PORT

fi