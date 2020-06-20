FROM spark_task

WORKDIR /usr/src/projection
COPY . /usr/src/projection

RUN pip install -r requirements.txt

ENV PROJECTION_HOST_NAME "projection"
ENV PROJECTION_HOST_PORT 5001
ENV PROJECTION_HOST_IP "0.0.0.0"
ENV SPARKMASTER_HOST "sparkmaster"
ENV SPARKMASTER_PORT 7077
ENV SPARK_DRIVER_PORT 41000

CMD ["python", "server.py"]