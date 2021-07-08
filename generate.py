import os
from collections import defaultdict

from jinja2 import Environment, FileSystemLoader, select_autoescape


class Generator:
    def __init__(self, pages_dir="pages", as_index=None, placeholder="placeholder.html"):
        self.as_index = as_index
        self.placeholder = placeholder
        self.adjacency = {}
        templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader([pages_dir, templates_dir]),
                               autoescape=False, trim_blocks=True, lstrip_blocks=True)

    @classmethod
    def from_HEdit(cls, graph_file, **kwargs):
        from HEdit.utils import json, HDict

        graph = HDict.load_from_path(graph_file)
        tp1, tp2, tp3 = graph.node_types()
        struct = graph.synthesize_structure(tp1, tp2, tp3)
        objects = graph.as_objects(tp1, tp2, tp3, struct)
        ins = cls(**kwargs)
        ins.adjacency = {o.id: o for o in objects}
        return ins

    def url_for(self, endpoint, **params):
        return f"/{endpoint.replace(' ', '-')*(endpoint != self.as_index)}{'?'*bool(params)}{'&'.join(f'{k}={v}' for k, v in params.items())}"

    def partitions_view(self, field_name):
        field_page_ids = defaultdict(list)
        for page in self.adjacency.values():
            field_page_ids[getattr(page, field_name)].append(page.id)

        base = self.env.get_template(f"partition.html")
        return base.render(pages=self.adjacency, url_for=self.url_for,
                           field_type="partition", field_name=field_name, field_page_ids=field_page_ids, fields=field_page_ids.keys())

    def labels_view(self, field_name):
        page_id_fields = {page.id: getattr(page, field_name) for page in self.adjacency.values()}
        fields = {f for fs in page_id_fields.values() for f in fs}

        base = self.env.get_template(f"label.html")
        return base.render(pages=self.adjacency, url_for=self.url_for,
                           field_type="label", field_name=field_name, page_id_fields=page_id_fields, fields=fields)

    def pages_view(self, page_id, link_fields, partition_fields, label_fields):
        base = self.env.get_template("page.html")
        return base.render(page=self.adjacency[page_id], pages=self.adjacency, url_for=self.url_for,
                           link_fields=link_fields, partition_fields=partition_fields, label_fields=label_fields,
                           main=f"{self.adjacency[page_id].data}.html", placeholder=self.placeholder)

    def generate(self, out_path, links=(), partitions=(), labels=()):
        for i, page in self.adjacency.items():
            filename = f"{'index' if page.data == self.as_index else page.data.replace(' ', '-')}.html"
            with open(os.path.join(out_path, filename), 'w') as f:
                f.write(self.pages_view(i, links, partitions, labels))

        for partition_name in partitions:
            with open(os.path.join(out_path, f"{partition_name}.html"), 'w') as f:
                f.write(self.partitions_view(partition_name))

        for label_name in labels:
            with open(os.path.join(out_path, f"{label_name}.html"), 'w') as f:
                f.write(self.labels_view(label_name))


if __name__ == '__main__':
    g = Generator.from_HEdit("site_graph.json", as_index="Home")
    g.generate("out", links=['related', 'inspired', 'subseded'], partitions=['date'], labels=['labels'])
