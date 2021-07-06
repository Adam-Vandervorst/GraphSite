from collections import defaultdict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from HEdit.utils import json, HDict


class Generator:
    def __init__(self, graph_file, pages_path="pages", out_path="out"):
        self.pages_path = pages_path
        self.out_path = out_path

        self.env = Environment(loader=FileSystemLoader(["templates", pages_path]),
                               autoescape=False, trim_blocks=True, lstrip_blocks=True)

        self.graph = HDict.load_from_path(graph_file)
        self.tp1, self.tp2, self.tp3 = self.graph.split_node_types()
        self.adjacency = self.graph.as_object_adjacency(self.tp1, self.tp2, self.tp3)

    def save(self, path):
        with open(path, 'w') as w_file:
            json.dump(self.adjacency, w_file)

    def partition_context(self, field_name):
        field_page_ids = defaultdict(list)
        for page in self.adjacency.values():
            field_page_ids[page[field_name]].append(page['id'])

        return dict(field_type="partition", field_name=field_name, field_page_ids=field_page_ids, fields=field_page_ids.keys())

    def label_context(self, field_name):
        page_id_fields = {page['id']: page[field_name] for page in self.adjacency.values()}
        fields = {f for fs in page_id_fields.values() for f in fs}

        return dict(field_type="label", field_name=field_name, page_id_fields=page_id_fields, fields=fields)

    @staticmethod
    def url_for(endpoint, **kwargs):
        return f"/{endpoint.replace(' ', '-')}{'?'*bool(kwargs)}{'&'.join(f'{k}={v}' for k, v in kwargs.items())}"

    def make_view(self, name, context_type):
        context = {
            'label': label_context,
            'partition': partition_context
        }[context_type](name)

        base = self.env.get_template(f"{context_type}.html")
        return base.render(**context, pages=self.adjacency, url_for=self.url_for)

    def pages_view(self, page_id):
        base = self.env.get_template("page.html")
        return base.render(**self.adjacency[page_id], pages=self.adjacency, main=f"{self.adjacency[page_id]['data']}.html", url_for=self.url_for)

    def generate(self, **show):
        for i, d in self.graph.get_info(self.tp3, 'id', 'data'):
            with open(f"{self.out_path}/{self.url_for(d)}.html", 'w') as f:
                f.write(self.pages_view(i))

        for i, d in self.graph.get_info(self.tp2, 'id', 'data'):
            if i in show:
                with open(f"{self.out_path}/{d}-view.html", 'w') as f:
                    f.write(self.make_view(d, show[d]))


if __name__ == '__main__':
    g = Generator("site_graph.json")
    g.generate(labels='label', date='partition')
