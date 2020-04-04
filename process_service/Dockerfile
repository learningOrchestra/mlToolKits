FROM python:3

ADD server.py /
WORKDIR /
RUN pip install flask

EXPOSE 5000

ENV FLASK_APP  server.py
ENTRYPOINT ["python", "-m", "flask", "run", "--host=0.0.0.0"]