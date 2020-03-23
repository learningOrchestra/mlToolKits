FROM python:3

ADD server.py /
WORKDIR /
RUN pip install flask

EXPOSE 5000

CMD [ "python", "server.py" ]