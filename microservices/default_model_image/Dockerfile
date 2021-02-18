FROM python:3.7-slim

WORKDIR /usr/src/default_model
COPY . /usr/src/default_model
RUN pip install -r requirements.txt

ENV DEFAULT_MODEL_HOST_IP "0.0.0.0"
ENV DEFAULT_MODEL_HOST_PORT 5007
ENV MODELS_VOLUME_PATH "/models"

CMD ["python", "server.py"]