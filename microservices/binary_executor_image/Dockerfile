FROM python:3.7-slim

WORKDIR /usr/src/binary_executor
COPY . /usr/src/binary_executor
RUN pip install -r requirements.txt

ENV MICROSERVICE_IP "0.0.0.0"
ENV MICROSERVICE_PORT 5008
ENV BINARY_VOLUME_PATH "/binaries"
ENV MODELS_VOLUME_PATH "/models"
ENV TRANSFORM_VOLUME_PATH "/transform"
ENV CODE_EXECUTOR_VOLUME_PATH "/code_executions"

CMD ["python", "server.py"]