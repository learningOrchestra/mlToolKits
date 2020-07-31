FROM spark_task

WORKDIR /usr/src/model_preprocessor
COPY . /usr/src/model_preprocessor

RUN pip install -r requirements.txt

ENV MODEL_PREPROCESSOR_HOST_NAME "modelpreprocessor"
ENV MODEL_PREPROCESSOR_HOST_PORT 5004
ENV MODEL_PREPROCESSOR_HOST_IP "0.0.0.0"
ENV SPARKMASTER_HOST "sparkmaster"
ENV SPARKMASTER_PORT 7077
ENV SPARK_DRIVER_PORT 41200

CMD ["python", "server.py"]