from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello_world():
    flask.app  # throw exception
    return "Hello Worggggld"


@app.route('/test')
def hi():
    return "Hiii"


if __name__ == '__main__':
    app.run(debug = True)
