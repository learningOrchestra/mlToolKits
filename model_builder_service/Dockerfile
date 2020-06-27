FROM spark_task

WORKDIR /usr/src/model_builder
COPY . /usr/src/model_builder

RUN pip install -r requirements.txt

ENV MODEL_BUILDER_HOST_NAME "model_builder"
ENV MODEL_BUILDER_HOST_PORT 5002
ENV MODEL_BUILDER_HOST_IP "0.0.0.0"
ENV SPARKMASTER_HOST "sparkmaster"
ENV SPARKMASTER_PORT 7077
ENV SPARK_DRIVER_PORT 41100

CMD ["python", "server.py"]