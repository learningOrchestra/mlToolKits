FROM python:3.6

RUN apt-get update && \
    apt-get install --no-install-recommends -y apt-transport-https ca-certificates wget dirmngr gnupg software-properties-common

RUN wget -qO - https://adoptopenjdk.jfrog.io/adoptopenjdk/api/gpg/key/public | apt-key add -

RUN add-apt-repository --yes https://adoptopenjdk.jfrog.io/adoptopenjdk/deb/

RUN apt-get update && \
    apt-get install --no-install-recommends -y adoptopenjdk-8-hotspot 

ENV SPARK_VERSION 2.4.7
ENV SPARK_INSTALL /usr/local
ENV SPARK_HOME $SPARK_INSTALL/spark
ENV HADOOP_VERSION 2.7
ENV PYSPARK_PYTHON python3
ENV PYSPARK_DRIVER_PYTHON python3

RUN curl -s http://mirror.synyx.de/apache/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz | tar -xz -C $SPARK_INSTALL && \
    cd $SPARK_INSTALL && ln -s spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION spark

RUN pip install pyspark==$SPARK_VERSION

RUN apt-get autoremove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

