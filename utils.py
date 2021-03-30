import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension

# First create the treeprocessor

class ImgExtractor(Treeprocessor):
    def run(self, doc):
        "Find all images and append to markdown.images. "
        self.markdown.images = []
        for image in doc.findall('.//img'):
            self.markdown.images.append(image.get('src'))

# Then tell markdown about it

class ImgExtExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        img_ext = ImgExtractor(md)
        md.treeprocessors.add('imgext', img_ext, '>inline')



class NameDescriptionExtractor(Treeprocessor):
    def run(self, doc):
        "Find all images and append to markdown.images. "
        self.markdown.h1s = []
        for h1 in doc.findall('.//h1'):
            self.markdown.h1s.append(h1.text)
        self.markdown.h2s = []
        for h2 in doc.findall('.//h2'):
            self.markdown.h2s.append(h2.text)


class H1H2Extension(Extension):
    def extendMarkdown(self, md, md_globals):
        h1h2_ext = NameDescriptionExtractor(md)
        md.treeprocessors.add('h1h2ext', h1h2_ext, '>inline')