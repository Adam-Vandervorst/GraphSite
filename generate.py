from collections import defaultdict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from HEdit.utils import json, HDict


class Generator:
    def __init__(self, graph_file, pages_path="pages", as_index=None):
        self.graph = HDict.load_from_path(graph_file)
        self.tp1, self.tp2, self.tp3 = self.graph.node_types()
        cls = self.graph.synthesize_structure(self.tp1, self.tp2, self.tp3)
        self.adjacency = {o.id: o for o in self.graph.as_objects(self.tp1, self.tp2, self.tp3, cls)}

        self.pages_path = pages_path
        self.as_index = as_index

        self.env = Environment(loader=FileSystemLoader(["templates", pages_path]),
                               autoescape=False, trim_blocks=True, lstrip_blocks=True)

    def save(self, path):
        with open(path, 'w') as w_file:
            json.dump(self.adjacency, w_file)

    def partition_context(self, field_name):
        field_page_ids = defaultdict(list)
        for page in self.adjacency.values():
            field_page_ids[getattr(page, field_name)].append(page.id)
        return dict(field_type="partition", field_name=field_name, field_page_ids=field_page_ids, fields=field_page_ids.keys())

    def label_context(self, field_name):
        page_id_fields = {page.id: getattr(page, field_name) for page in self.adjacency.values()}
        fields = {f for fs in page_id_fields.values() for f in fs}
        return dict(field_type="label", field_name=field_name, page_id_fields=page_id_fields, fields=fields)

    def url_for(self, endpoint, **params):
        return f"/{endpoint.replace(' ', '-')*(endpoint != self.as_index)}{'?'*bool(params)}{'&'.join(f'{k}={v}' for k, v in params.items())}"

    def make_view(self, name, context_type):
        context = {'label': self.label_context, 'partition': self.partition_context}[context_type](name)
        base = self.env.get_template(f"{context_type}.html")
        return base.render(**context, pages=self.adjacency, url_for=self.url_for)

    def pages_view(self, page_id):
        base = self.env.get_template("page.html")
        return base.render(page=self.adjacency[page_id], pages=self.adjacency, main=f"{self.adjacency[page_id].data}.html", url_for=self.url_for)

    def generate(self, out_path, **show):
        for i, d in self.graph.get_info(self.tp3, 'id', 'data'):
            with open(f"{out_path}/{'index' if d == self.as_index else d}.html", 'w') as f:
                f.write(self.pages_view(i))

        for i, d in self.graph.get_info(self.tp2, 'id', 'data'):
            if d in show:
                with open(f"{out_path}/{d}-view.html", 'w') as f:
                    f.write(self.make_view(d, show[d]))


if __name__ == '__main__':
    g = Generator("site_graph.json", as_index="Home")
    g.generate("out", labels='label', date='partition')
