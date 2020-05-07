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
    print(request.form['cpf'])
    body = {
        "filename": request.form['filename'],
        "url": request.form["url"]
    }

    response = requests.post(str(DATABASE_API_HOST) + ":" +
                             str(DATABASE_API_PORT) +
                             "/add", json=body)
    json_object = json.loads(json.dumps(response.json()))
    return json.dumps(json_object, indent=2)


if __name__ == '__main__':
    app.run(host=os.environ["FRONTEND_SERVER_HOST"],
            port=int(os.environ["FRONTEND_SERVER_PORT"]))
