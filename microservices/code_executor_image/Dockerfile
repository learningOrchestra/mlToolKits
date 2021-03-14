FROM python:3.7-slim

WORKDIR /usr/src/code_executor
COPY . /usr/src/code_executor

RUN pip install -r requirements.txt

ENV MICROSERVICE_IP "0.0.0.0"
ENV MICROSERVICE_PORT 5009
ENV EXPLORE_VOLUME_PATH "/explore"
ENV TRANSFORM_VOLUME_PATH "/transform"
ENV BINARY_VOLUME_PATH "/binaries"
ENV MODELS_VOLUME_PATH "/models"
ENV CODE_EXECUTOR_VOLUME_PATH "/code_executions"
ENV DATASET_VOLUME_PATH "/datasets"

CMD ["python", "server.py"]