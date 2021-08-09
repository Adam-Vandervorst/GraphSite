from markdown import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

from urllib.parse import urlparse


class ProcessLinks(Extension, Treeprocessor):
    def __init__(self, valid_names, missing_pages_class=None, external_new_tab=False, internal_field=None):
        super().__init__()
        self.valid_names = valid_names
        self.missing_pages_class = missing_pages_class
        self.internal_field = internal_field
        self.ops = []
        self.current_name = None

        if missing_pages_class:
            self.ops.append(self.tag_missing)
        if external_new_tab:
            self.ops.append(self.external_new_tab)
        if internal_field:
            self.ops.append(self.connect_internal)
            for page in valid_names.values():
                if not hasattr(page, internal_field):
                    setattr(page, internal_field, [])

    def run(self, root):
        for anchor in root.findall('.//a'):
            url = urlparse(anchor.attrib['href'])
            for op in self.ops:
                op(url, anchor)

    def tag_missing(self, url, anchor):
        if not url.netloc and url.path not in self.valid_names:
            anchor.attrib['class'] = self.missing_pages_class

    def external_new_tab(self, url, anchor):
        if url.netloc:
            anchor.attrib['target'] = "_blank"

    def connect_internal(self, url, anchor):
        if not url.netloc and url.path in self.valid_names:
            links = getattr(self.valid_names[self.current_name], self.internal_field, [])
            links.append(self.valid_names[url.path])

    def extendMarkdown(self, md):
        md.treeprocessors.register(self, 'processlinks', -100)
