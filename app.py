import flask
from flask import Flask

app = Flask(__name__, static_url_path='', static_folder='static')


@app.route('/')
def hello_world():
    return flask.render_template("main.html")


if __name__ == '__main__':
    app.run(debug=True)
