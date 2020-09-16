FROM spark_task

WORKDIR /usr/src/pca
COPY . /usr/src/pca

RUN pip install -r requirements.txt

ENV PCA_HOST_NAME "pca"
ENV PCA_HOST_PORT 5006
ENV PCA_HOST_IP "0.0.0.0"
ENV SPARKMASTER_HOST "sparkmaster"
ENV SPARKMASTER_PORT 7077
ENV SPARK_DRIVER_PORT 41300
ENV IMAGES_PATH "/images"
CMD ["python", "server.py"]