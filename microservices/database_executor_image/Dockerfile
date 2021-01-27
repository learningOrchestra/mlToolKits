FROM python:3.7-slim

WORKDIR /usr/src/database_executor
COPY . /usr/src/database_executor

RUN pip install -r requirements.txt

ENV MICROSERVICE_IP "0.0.0.0"
ENV MICROSERVICE_PORT 5006
ENV IMAGES_VOLUME_PATH "/images"
ENV TRANSFORM_VOLUME_PATH "/transform"
CMD ["python", "server.py"]