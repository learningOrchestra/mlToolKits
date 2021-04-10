FROM python:3.7-slim

WORKDIR /usr/src/model
COPY . /usr/src/model
RUN pip install -r requirements.txt

ENV DEFAULT_MODEL_HOST_IP "0.0.0.0"
ENV DEFAULT_MODEL_HOST_PORT 5007

ENV EXPLORE_VOLUME_PATH "/explore"
ENV TRANSFORM_VOLUME_PATH "/transform"
ENV BINARY_VOLUME_PATH "/binaries"
ENV MODELS_VOLUME_PATH "/models"
ENV CODE_EXECUTOR_VOLUME_PATH "/code_executions"

CMD ["python", "server.py"]