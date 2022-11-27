from urllib.parse import urlparse

from markdown import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.postprocessors import Postprocessor


class CodeProcessor(Postprocessor):
    def run(self, text):
        return text.replace(self.wbr, "<wbr>")


class ProcessLinks(Extension, Treeprocessor):
    wbr_after = tuple(',;:_=({[')
    wbr_before = tuple('.)}]')
    wbr = "WORDBREAKOPPORTUNITY"

    def __init__(self, name_exists, id_titles=(), missing_pages_class=None, external_new_tab=False, collect_internal=False, wbr_code=False):
        super().__init__()
        self.name_exists = name_exists
        self.id_titles = id_titles
        self.missing_pages_class = missing_pages_class
        self.external_new_tab = external_new_tab
        self.collect_internal = collect_internal
        self.wbr_code = wbr_code
        self.collected = []

    def run(self, root):
        for title_number in self.id_titles:
            for h_elem in root.findall(f'.//h{title_number}'):
                self.id_h(h_elem)

        for anchor in root.findall('.//a'):
            url = urlparse(anchor.attrib['href'])
            if self.missing_pages_class: self.missing(url, anchor)
            if self.external_new_tab: self.new_tab(url, anchor)
            if self.collect_internal: self.internal(url, anchor)

        for code_elem in root.findall('.//code'):
            if self.wbr_code: self.code(code_elem)

    def missing(self, url, anchor):
        if not url.netloc and url.path in self.name_exists and not any(self.name_exists[url.path]):
            anchor.attrib['class'] = self.missing_pages_class

    def new_tab(self, url, anchor):
        if url.netloc:
            anchor.attrib['target'] = "_blank"

    def internal(self, url, anchor):
        if not url.netloc and url.path in self.name_exists:
            self.collected.append(url.path)

    def id_h(self, h_elem):
        h_elem.attrib['id'] = h_elem.text

    def code(self, code_elem):
        s = code_elem.text
        for c in self.wbr_after: s = s.replace(c, c + self.wbr)
        for c in self.wbr_before: s = s.replace(c, self.wbr + c)
        s = s.replace(' ' + self.wbr, ' ').replace(self.wbr + ' ', ' ')
        code_elem.text = s.replace(self.wbr*2, '')

    def extendMarkdown(self, md):
        md.treeprocessors.register(self, "processlinks", -100)
        if self.wbr_code:
            code_processor = CodeProcessor()
            code_processor.wbr = self.wbr
            md.postprocessors.register(code_processor, "GraphSite-PostProcessor", -100)
