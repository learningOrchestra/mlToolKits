FROM spark_task

WORKDIR /usr/src/tsne
COPY . /usr/src/tsne

RUN pip install -r requirements.txt

ENV TSNE_HOST_NAME "tsne"
ENV TSNE_HOST_PORT 5005
ENV TSNE_HOST_IP "0.0.0.0"
ENV SPARKMASTER_HOST "sparkmaster"
ENV SPARKMASTER_PORT 7077
ENV SPARK_DRIVER_PORT 41200

CMD ["python", "server.py"]