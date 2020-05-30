FROM python:3.7.7

RUN apt-get update && \
    apt-get install -y openjdk-11-jdk

WORKDIR /usr/src/projection
COPY . /usr/src/projection
RUN pip install -r requirements.txt

ENV PROJECTION_HOST "0.0.0.0"
ENV PROJECTION_PORT 5001

CMD ["python", "server.py"]