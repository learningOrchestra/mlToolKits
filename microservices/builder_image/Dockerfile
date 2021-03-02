FROM spark_task

WORKDIR /usr/src/builder
COPY . /usr/src/builder

RUN pip install -r requirements.txt

ENV BUILDER_HOST_NAME "builder"
ENV BUILDER_HOST_PORT 5002
ENV BUILDER_HOST_IP "0.0.0.0"
ENV SPARKMASTER_HOST "sparkmaster"
ENV SPARKMASTER_PORT 7077
ENV SPARK_DRIVER_PORT 41100

CMD ["python", "server.py"]