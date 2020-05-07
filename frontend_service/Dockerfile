FROM python:3

WORKDIR /usr/src/frontend
COPY . /usr/src/frontend
RUN pip install -r requirements.txt

ENV FRONTEND_SERVER_HOST "0.0.0.0"
ENV FRONTEND_SERVER_PORT 8000

ENV DATABASE_API_HOST "0.0.0.0"
ENV DATABASE_API_PORT 5000

CMD ["python", "server.py"]