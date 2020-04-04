FROM python:3

ADD mongo_api.py /
WORKDIR /
COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 5000

ENV FLASK_APP  mongo_api.py
ENTRYPOINT ["python", "-m", "flask", "run", "--host=0.0.0.0"]