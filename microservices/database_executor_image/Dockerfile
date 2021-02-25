FROM python:3.7-slim

WORKDIR /usr/src/database_executor
COPY . /usr/src/database_executor

RUN pip install -r requirements.txt

ENV MICROSERVICE_IP "0.0.0.0"
ENV MICROSERVICE_PORT 5006
ENV EXPLORE_VOLUME_PATH "/explore"
ENV TRANSFORM_VOLUME_PATH "/transform"
ENV BINARY_VOLUME_PATH "/binaries"
ENV MODELS_VOLUME_PATH "/models"
ENV CODE_EXECUTOR_VOLUME_PATH "/code_executions"

CMD ["python", "server.py"]