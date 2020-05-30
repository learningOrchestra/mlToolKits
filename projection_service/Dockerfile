FROM python:3.7.7

WORKDIR /usr/src/projection
COPY . /usr/src/projection
RUN pip install -r requirements.txt

ENV PROJECTION_HOST "0.0.0.0"
ENV PROJECTION_PORT 5001

CMD ["python", "server.py"]