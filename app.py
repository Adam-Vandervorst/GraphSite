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


@app.route('/timeline', defaults={'date': '2021'})
@app.route('/timeline/<date>')
def timeline_view(date):
    date_page_ids = defaultdict(list)
    for page in adjacency.values():
        date_page_ids[page['date']].append(page['id'])
    if date not in date_page_ids:
        return flask.redirect("/timeline")
    from_page_id = flask.request.args.get('from_id', None, int)
    return flask.render_template("timeline.html", chosen_date=date, date_page_ids=date_page_ids, from_page_id=from_page_id, pages=adjacency)


@app.route('/labels', defaults={'label': 'highlight'})
@app.route('/labels/<label>')
def labels_view(label):
    labels_page_ids = defaultdict(list)
    for page in adjacency.values():
        for page_label in page['labels']:
            labels_page_ids[page_label].append(page['id'])
    if label not in labels_page_ids:
        return flask.redirect("/labels")
    from_page_id = flask.request.args.get('from_id', None, int)
    return flask.render_template("labels.html", chosen_label=label, labels_page_ids=labels_page_ids, from_page_id=from_page_id, pages=adjacency)


if __name__ == '__main__':
    app.run(debug=True)
