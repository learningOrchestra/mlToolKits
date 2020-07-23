FROM python:3.6-slim

WORKDIR /usr/src/data_type_handler
COPY . /usr/src/data_type_handler
RUN pip install -r requirements.txt

ENV DATA_TYPE_HANDLER_HOST "0.0.0.0"
ENV DATA_TYPE_HANDLER_PORT 5003

CMD ["python", "server.py"]