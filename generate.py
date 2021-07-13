import os
from collections import defaultdict

from jinja2 import Environment, FileSystemLoader, select_autoescape


class Generator:
    def __init__(self, pages_dir="pages", as_index=None, placeholder="placeholder.html"):
        self.pages_dir = pages_dir
        self.as_index = as_index
        self.placeholder = placeholder
        self.pages = []
        templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader([pages_dir, templates_dir]),
                               autoescape=False, trim_blocks=True, lstrip_blocks=True)

    @classmethod
    def from_HEdit(cls, graph_file, **kwargs):
        from HEdit.utils import json, HDict

        graph = HDict.load_from_path(graph_file)
        tp1, tp2, tp3 = graph.node_types()
        struct = graph.synthesize_structure(tp1, tp2, tp3)
        struct.__lt__ = lambda x, y: x.data < y.data
        ins = cls(**kwargs)
        ins.pages = graph.as_objects(tp1, tp2, tp3, struct)
        return ins

    def convert_markdown(self, ignore_list=(), **md_options):
        from markdown import markdown

        for page in self.pages:
            name = page.data.replace(' ', '-')
            if name in ignore_list: continue
            in_path = os.path.join(self.pages_dir, f"{name}.md")
            out_path = os.path.join(self.pages_dir, f"{name}.html")
            if not os.path.exists(in_path): continue
            with open(in_path, 'r') as in_f, open(out_path, 'w') as out_f:
                out_f.write(markdown(in_f.read(), **md_options))

    def url_for(self, endpoint, **params):
        url_params = '&'.join(f'{k}={v}' for k, vs in params.items() for v in (vs if isinstance(vs, tuple) else (vs,)))
        return f"/{endpoint.replace(' ', '-')*(endpoint != self.as_index)}{'?'*bool(params)}{url_params}"

    def partitions_view(self, field_name):
        field_pages = defaultdict(list)
        for page in self.pages:
            field_pages[getattr(page, field_name)].append(page)

        base = self.env.get_template(f"partition.html")
        return base.render(url_for=self.url_for, field_type="partition",
                           field_name=field_name, field_pages=field_pages.items(), fields=field_pages.keys())

    def labels_view(self, field_name):
        page_fields = [(page, getattr(page, field_name)) for page in self.pages]
        fields = {f for _, fs in page_fields for f in fs}

        base = self.env.get_template(f"label.html")
        return base.render(url_for=self.url_for, field_type="label",
                           field_name=field_name, page_fields=page_fields, fields=fields)

    def pages_view(self, page, link_fields, partition_fields, label_fields):
        base = self.env.get_template("page.html")
        return base.render(page=page, url_for=self.url_for,
                           link_fields=link_fields, partition_fields=partition_fields, label_fields=label_fields,
                           main=f"{page.data.replace(' ', '-')}.html", placeholder=self.placeholder)

    def generate(self, out_path, links=(), partitions=(), labels=()):
        for page in self.pages:
            filename = f"{'index' if page.data == self.as_index else page.data.replace(' ', '-')}.html"
            with open(os.path.join(out_path, filename), 'w') as f:
                f.write(self.pages_view(page, links, partitions, labels))

        for partition_name in partitions:
            with open(os.path.join(out_path, f"{partition_name}.html"), 'w') as f:
                f.write(self.partitions_view(partition_name))

        for label_name in labels:
            with open(os.path.join(out_path, f"{label_name}.html"), 'w') as f:
                f.write(self.labels_view(label_name))


if __name__ == '__main__':
    g = Generator.from_HEdit("site_graph.json", as_index="Home")
    g.convert_markdown()
    g.generate("out", links=['related', 'inspired', 'subseded'], partitions=['date'], labels=['labels'])
