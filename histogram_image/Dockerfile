FROM python:3.6-slim

WORKDIR /usr/src/histogram
COPY . /usr/src/histogram
RUN pip install -r requirements.txt

ENV HISTOGRAM_HOST "0.0.0.0"
ENV HISTOGRAM_PORT 5004

CMD ["python", "server.py"]