import flask
from flask import Flask

from HEdit.utils import json, HDict


site_graph = HDict.load_from_path("site_graph.json")
page_objects = {}
for page_node in site_graph.as_objects():
    del page_node['id']
    name = page_node.pop('data')
    page_objects[name] = page_node

with open("./static/generated_objects.json", 'w') as f:
    json.dump(page_objects, f)


app = Flask(__name__, static_url_path='', static_folder='static')


@app.route('/')
def hello_world():
    return flask.render_template("main.html")


if __name__ == '__main__':
    app.run(debug=True)
