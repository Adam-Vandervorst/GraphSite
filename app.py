from collections import defaultdict

import flask

from HEdit.utils import json, HDict


graph = HDict.load_from_path("site_graph.json")
tp1, tp2, tp3 = graph.split_node_types()
print(tp2)
adjacency = graph.as_object_adjacency(tp1, tp2, tp3)

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


def make_view(name, context_type):
    context = {
        'label': label_context,
        'partition': partition_context
    }[context_type](name)

    @app.route(f"/{name}", endpoint=f"{name}_view", methods=['GET'])
    def view():
        return flask.render_template(f"{context_type}.html", **context, pages=adjacency)
    return view


app = flask.Flask(__name__, static_url_path='', static_folder='static')


@app.route('/', defaults={'page_id': 0})
@app.route('/pages/<int:page_id>')
def pages_view(page_id):
    return flask.render_template(f"/pages/{adjacency[page_id]['data']}.html", **adjacency[page_id], pages=adjacency)


show = {8: 'label', 4: 'partition'}


for i, d in graph.get_info(tp2, 'id', 'data'):
    if i in show:
        make_view(d, show[i])

if __name__ == '__main__':
    app.run(debug=True)
