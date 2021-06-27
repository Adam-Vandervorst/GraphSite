from collections import defaultdict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from HEdit.utils import json, HDict


graph = HDict.load_from_path("site_graph.json")
tp1, tp2, tp3 = graph.split_node_types()
adjacency = graph.as_object_adjacency(tp1, tp2, tp3)

with open("generated_objects.json", 'w') as w_file:
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


def url_for(endpoint, **kwargs):
    return f"/{endpoint.replace(' ', '-')}{'?'*bool(kwargs)}{'&'.join(f'{k}={v}' for k, v in kwargs.items())}"


def make_view(name, context_type):
    context = {
        'label': label_context,
        'partition': partition_context
    }[context_type](name)

    base = env.get_template(f"{context_type}.html")
    return base.render(**context, pages=adjacency, url_for=url_for)


def pages_view(page_id):
    base = env.get_template("page.html")
    return base.render(**adjacency[page_id], pages=adjacency, main=f"{adjacency[page_id]['data']}.html", url_for=url_for)


if __name__ == '__main__':
    pages_path = "pages"
    out_path = "out"

    env = Environment(
        loader=FileSystemLoader(["templates", pages_path]),
        autoescape=False,
        trim_blocks=True, lstrip_blocks=True
    )

    for i, d in graph.get_info(tp3, 'id', 'data'):
        with open(f"{out_path}/{url_for(d)}.html", 'w') as f:
            f.write(pages_view(i))

    show = {8: 'label', 4: 'partition'}

    for i, d in graph.get_info(tp2, 'id', 'data'):
        if i in show:
            with open(f"{out_path}/{d}-view.html", 'w') as f:
                f.write(make_view(d, show[i]))
