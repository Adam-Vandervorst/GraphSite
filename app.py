from collections import defaultdict

import flask

from HEdit.utils import json, HDict


graph = HDict.load_from_path("site_graph.json")
adjacency = graph.as_object_adjacency(*graph.split_node_types())

with open("./static/generated_objects.json", 'w') as f:
    json.dump(adjacency, f)


app = flask.Flask(__name__, static_url_path='', static_folder='static')


@app.route('/', defaults={'page_id': 0})
@app.route('/pages/<int:page_id>')
def pages_view(page_id):
    return flask.render_template(f"/pages/{adjacency[page_id]['data']}.html", **adjacency[page_id], pages=adjacency)


date_page_ids = defaultdict(list)
for page in adjacency.values():
    date_page_ids[page['date']].append(page['id'])

field_type_context = dict(
    field_name="date",
    field_page_ids=date_page_ids
)


@app.route('/date')
def date_view():
    overview_context = dict(
        from_page_id=flask.request.args.get('from_id', None, int),
        filters=flask.request.args.getlist('filter')
    )
    return flask.render_template("one_to_many.html", **overview_context, **field_type_context, pages=adjacency)


labels_page_ids = defaultdict(list)
for page in adjacency.values():
    for page_label in page['labels']:
        labels_page_ids[page_label].append(page['id'])

field_type_context = dict(
    field_name="labels",
    field_page_ids=labels_page_ids
)


@app.route('/labels')
def labels_view():
    overview_context = dict(
        from_page_id=flask.request.args.get('from_id', None, int),
        filters=flask.request.args.getlist('filter')
    )
    return flask.render_template("one_to_many.html", **overview_context, **field_type_context, pages=adjacency)


if __name__ == '__main__':
    app.run(debug=True)
