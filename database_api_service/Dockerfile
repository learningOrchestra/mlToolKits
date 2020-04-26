FROM python:3

ADD database_api.py /
WORKDIR /
COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 5000

ENV FLASK_APP  database_api.py
ENTRYPOINT ["python", "-m", "flask", "run", "--host=0.0.0.0"]