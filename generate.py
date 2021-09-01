import os
from collections import defaultdict

from jinja2 import Environment, FileSystemLoader


class Generator:
    def __init__(self, pages_dir="pages", as_index=None, placeholder="placeholder.html", safe_name=lambda s: s.replace(' ', '-')):
        self.pages_dir = pages_dir
        self.as_index = as_index
        self.placeholder = placeholder
        self.safe_name = safe_name
        self.pages = []
        self.contact = []
        self.info = {"name_field": None, "description_field": None}
        self.structure = {"link_fields": [], "partition_fields": [], "label_fields": []}
        templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader([pages_dir, templates_dir]),
                               autoescape=False, trim_blocks=True, lstrip_blocks=True)

    @classmethod
    def from_HEdit(cls, graph_file, custom_page_cls=None, **kwargs):
        from HEdit.utils import json, HDict

        graph = HDict.load_from_path(graph_file)
        tp1, tp2, tp3 = graph.node_types()
        if custom_page_cls:
            page_cls = custom_page_cls
        else:
            struct = graph.synthesize_structure(tp1, tp2, tp3, "Page")
            page_cls = type("Page", (struct,), {'__lt__': lambda x, y: x.data < y.data})
        ins = cls(**kwargs)
        ins.add_pages(graph.as_objects(tp1, tp2, tp3, page_cls))
        return ins

    def convert_markdown(self, missing_pages_class="missing", external_new_tab=True, internal_field=None):
        from process import markdown, ProcessLinks

        name_page = {self.safe_name(page.data): page for page in self.pages}
        name_paths = {name: (os.path.join(self.pages_dir, f"{name}.md"), os.path.join(self.pages_dir, f"{name}.html")) for name in name_page}
        name_exists = {name: (os.path.exists(md), os.path.exists(html)) for name, (md, html) in name_paths.items()}
        transformation = ProcessLinks(name_exists, missing_pages_class, external_new_tab, internal_field is not None)

        for name, (in_path, out_path) in name_paths.items():
            transformation.collected = []
            if name_exists[name][0]:
                with open(in_path, 'r') as in_f, open(out_path, 'w') as out_f:
                    out_f.write(markdown(in_f.read(), extensions=[transformation]))
            if internal_field:
                setattr(name_page[name], internal_field, [name_page[name] for name in transformation.collected])

    def add_pages(self, pages):
        self.pages.extend(pages)

    def add_contact(self, links):
        self.contact.extend(links)

    def add_info(self, name=None, description=None):
        if name: self.info['name_field'] = name
        if description: self.info['description_field'] = description

    def add_structure(self, links=(), partitions=(), labels=()):
        self.structure["link_fields"].extend(links)
        self.structure["partition_fields"].extend(partitions)
        self.structure["label_fields"].extend(labels)

    def url_for(self, endpoint, **params):
        url_params = '&'.join(f'{k}={v}' for k, vs in params.items()
                              for v in (vs if isinstance(vs, (tuple, list, set)) else (vs,)))
        return f"/{self.safe_name(endpoint)*(endpoint != self.as_index)}{'?'*bool(params)}{url_params}"

    def partitions_view(self, field_name):
        field_pages = defaultdict(list)
        for page in self.pages:
            field_pages[getattr(page, field_name)].append(page)

        base = self.env.get_template(f"partition.html")
        return base.render(url_for=self.url_for, contact=self.contact, field_type="partition", **self.info,
                           field_name=field_name, field_pages=field_pages.items(), fields=field_pages.keys())

    def labels_view(self, field_name):
        page_fields = [(page, getattr(page, field_name)) for page in self.pages]
        fields = {f for _, fs in page_fields for f in fs}

        base = self.env.get_template(f"label.html")
        return base.render(url_for=self.url_for, contact=self.contact, field_type="label", **self.info,
                           field_name=field_name, page_fields=page_fields, fields=fields)

    def pages_view(self, page):
        base = self.env.get_template("page.html")
        return base.render(page=page, url_for=self.url_for, contact=self.contact, **self.info, **self.structure,
                           main=f"{self.safe_name(page.data)}.html", placeholder=self.placeholder)

    def generate(self, out_path):
        for page in self.pages:
            filename = f"{'index' if page.data == self.as_index else self.safe_name(page.data)}.html"
            with open(os.path.join(out_path, filename), 'w') as f:
                f.write(self.pages_view(page))

        for partition_name in self.structure["partition_fields"]:
            with open(os.path.join(out_path, f"{partition_name}.html"), 'w') as f:
                f.write(self.partitions_view(partition_name))

        for label_name in self.structure["label_fields"]:
            with open(os.path.join(out_path, f"{label_name}.html"), 'w') as f:
                f.write(self.labels_view(label_name))


if __name__ == '__main__':
    g = Generator.from_HEdit("site_graph.json", as_index="Home")
    g.convert_markdown()
    g.add_contact([("Github repo", "https://github.com/Adam-Vandervorst/GraphSite"), ("Landing page", "/")])
    g.add_info(name='data', description='description')
    g.add_structure(links=['related', 'inspired', 'subseded'], partitions=['date'], labels=['labels'])
    g.generate("out")
