import requests
import json
from flask import Flask, render_template, request
import os

app = Flask(__name__)


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/send-file', methods=['POST'])
def send_file():
    body = {
        "filename": request.form['filename'],
        "url": request.form["url"]
    }

    response = requests.post(os.environ["DATABASE_API_HOST"] +
                             ":" + str(os.environ["DATABASE_API_PORT"]) +
                             "/add", json=body)

    return response.text


if __name__ == '__main__':
    app.run(host=os.environ["FRONTEND_SERVER_HOST"],
            port=int(os.environ["FRONTEND_SERVER_PORT"]))
