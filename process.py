from markdown import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

from urllib.parse import urlparse


class ProcessLinks(Extension, Treeprocessor):
    def __init__(self, name_exists, missing_pages_class=None, external_new_tab=False, collect_internal=False):
        super().__init__()
        self.name_exists = name_exists
        self.missing_pages_class = missing_pages_class
        self.collected = []
        self.ops = []

        if missing_pages_class:
            self.ops.append(self.tag_missing)
        if external_new_tab:
            self.ops.append(self.external_new_tab)
        if collect_internal:
            self.ops.append(self.collect_internal)

    def run(self, root):
        for anchor in root.findall('.//a'):
            url = urlparse(anchor.attrib['href'])
            for op in self.ops:
                op(url, anchor)

    def tag_missing(self, url, anchor):
        if not url.netloc and url.path in self.name_exists and not any(self.name_exists[url.path]):
            anchor.attrib['class'] = self.missing_pages_class

    def external_new_tab(self, url, anchor):
        if url.netloc:
            anchor.attrib['target'] = "_blank"

    def collect_internal(self, url, anchor):
        if not url.netloc and url.path in self.name_exists:
            self.collected.append(url.path)

    def extendMarkdown(self, md):
        md.treeprocessors.register(self, 'processlinks', -100)
