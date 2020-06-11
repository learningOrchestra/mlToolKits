FROM python:3.5

RUN apt update && \
    apt install -y apt-transport-https ca-certificates wget dirmngr gnupg software-properties-common

RUN wget -qO - https://adoptopenjdk.jfrog.io/adoptopenjdk/api/gpg/key/public | apt-key add -

RUN add-apt-repository --yes https://adoptopenjdk.jfrog.io/adoptopenjdk/deb/

RUN apt update && \
    apt install -y adoptopenjdk-8-hotspot


WORKDIR /usr/src/projection
COPY . /usr/src/projection

RUN pip install -r requirements.txt
RUN pyspark --packages org.mongodb.spark:mongo-spark-connector_2.11:2.4.1

ENV PROJECTION_HOST_NAME "projection"
ENV PROJECTION_HOST_PORT 5001
ENV PROJECTION_HOST_IP "0.0.0.0"
ENV SPARK_LOCAL_IP "0.0.0.0"
ENV SPARKMASTER_HOST "sparkmaster"
ENV SPARKMASTER_PORT 7077
ENV SPARK_DRIVER_PORT 41000

ENV SPARK_VERSION 2.4.5
ENV SPARK_INSTALL /usr/local
ENV SPARK_HOME $SPARK_INSTALL/spark
ENV HADOOP_VERSION 2.7
ENV PYSPARK_PYTHON python3
ENV PYSPARK_DRIVER_PYTHON python3

RUN curl -s http://mirror.synyx.de/apache/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz | tar -xz -C $SPARK_INSTALL && \
    cd $SPARK_INSTALL && ln -s spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION spark

RUN pyspark --packages org.mongodb.spark:mongo-spark-connector_2.11:2.4.1
RUN sudo -- sh -c "echo '0.0.0.0 projection' >> /etc/hosts"
CMD ["python", "server.py"]