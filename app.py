import flask
from flask import Flask

from HEdit.utils import json, HDict


def convert_graph(path):
    graph = HDict.load_from_path(path)
    adjacency = graph.as_object_adjacency(*graph.split_node_types())

    with open("./static/generated_objects.json", 'w') as f:
        json.dump(adjacency, f)


convert_graph("site_graph.json")
app = Flask(__name__, static_url_path='', static_folder='static')


@app.route('/')
def hello_world():
    return flask.render_template("main.html", start_id=0)


if __name__ == '__main__':
    app.run(debug=True)
