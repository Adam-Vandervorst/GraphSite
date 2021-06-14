from collections import defaultdict

import flask

from HEdit.utils import json, HDict


graph = HDict.load_from_path("site_graph.json")
adjacency = graph.as_object_adjacency(*graph.split_node_types())

with open("./static/generated_objects.json", 'w') as w_file:
    json.dump(adjacency, w_file)


def partition_context(field_name):
    field_page_ids = defaultdict(list)
    for page in adjacency.values():
        field_page_ids[page[field_name]].append(page['id'])

    return dict(field_type="partition", field_name=field_name, field_page_ids=field_page_ids, fields=field_page_ids.keys())


def label_context(field_name):
    page_id_fields = {page['id']: page[field_name] for page in adjacency.values()}
    fields = {f for fs in page_id_fields.values() for f in fs}

    return dict(field_type="label", field_name=field_name, page_id_fields=page_id_fields, fields=fields)


app = flask.Flask(__name__, static_url_path='', static_folder='static')


@app.route('/', defaults={'page_id': 0})
@app.route('/pages/<int:page_id>')
def pages_view(page_id):
    return flask.render_template(f"/pages/{adjacency[page_id]['data']}.html", **adjacency[page_id], pages=adjacency)


date_context = partition_context('date')
@app.route('/date')
def date_view():
    overview_context = dict(
        from_page_id=flask.request.args.get('from_id', None, int),
        filters=flask.request.args.getlist('filter')
    )
    return flask.render_template("partition.html", **date_context, **overview_context, pages=adjacency)


labels_context = label_context('labels')
@app.route('/labels')
def labels_view():
    overview_context = dict(
        from_page_id=flask.request.args.get('from_id', None, int),
        filters=flask.request.args.getlist('filter')
    )
    return flask.render_template("label.html", **labels_context, **overview_context, pages=adjacency)


if __name__ == '__main__':
    app.run(debug=True)
