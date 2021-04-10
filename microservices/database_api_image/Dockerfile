FROM python:3.7-slim

WORKDIR /usr/src/database_api
COPY . /usr/src/database_api
RUN pip install -r requirements.txt

ENV DATABASE_API_HOST "0.0.0.0"
ENV DATABASE_API_PORT 5000

ENV DATASET_VOLUME_PATH "/datasets"

CMD ["python", "server.py"]