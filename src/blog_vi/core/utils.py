import csv
import hashlib
import os
import shutil
from pathlib import Path

import requests
from markdown import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.blockprocessors import BlockProcessor
from markdown.util import etree


class ImgExtractor(Treeprocessor):
    def run(self, doc):
        """Find all images and append to markdown.images."""
        self.markdown.images = []
        for image in doc.findall('.//img'):
            self.markdown.images.append(image.get('src'))


class ImgExtExtension(Extension):
    def extendMarkdown(self, md):
        img_ext = ImgExtractor(md)
        md.treeprocessors.add('imgext', img_ext, '>inline')


class NameDescriptionExtractor(Treeprocessor):
    def run(self, doc):
        """Find all h1,h2 and append to markdown.h1 and markdown.h2."""
        self.markdown.h1s = []
        for h1 in doc.findall('.//h1'):
            self.markdown.h1s.append(h1.text)
        self.markdown.h2s = []
        for h2 in doc.findall('.//h2'):
            self.markdown.h2s.append(h2.text)


class H1H2Extension(Extension):
    def extendMarkdown(self, md):
        h1h2_ext = NameDescriptionExtractor(md)
        md.treeprocessors.add('h1h2ext', h1h2_ext, '>inline')


class TableProcessor(BlockProcessor):
    """Converts Markdown tables to HTML tables"""

    def run(self, parent, blocks):
        """Converts the table block to an HTML table"""
        block = blocks.pop(0).strip()
        table = etree.SubElement(parent, 'table')
        thead = etree.SubElement(table, 'thead')
        tbody = etree.SubElement(table, 'tbody')
        rows = block.split('\n')
        headers = rows.pop(0).strip('|').split('|')
        for header in headers:
            etree.SubElement(thead, 'th').text = header.strip()
        for row in rows:
            cells = row.strip('|').split('|')
            tr = etree.SubElement(tbody, 'tr')
            for cell in cells:
                etree.SubElement(tr, 'td').text = cell.strip()


class MarkdownTableExtension(Extension):
    """A Markdown extension that converts tables to HTML"""

    def extendMarkdown(self, md):
        """Adds the TableProcessor to the Markdown instance"""
        md.parser.blockprocessors.register(TableProcessor(md.parser), 'table', 175)


def make_json(file: str) -> list:
    data = []
    # read records from data.csv file and convert it list
    with open(file, encoding='utf-8') as f:
        csvReader = csv.DictReader(f)
        for rows in csvReader:
            data.append(rows)
    return data


def get_articles_from_csv(url: str) -> list:
    response = requests.get(url=url)
    # write records to data.csv file
    with open('data.csv', 'wb') as f:
        f.write(response.content)

    return make_json('data.csv')


def get_md_file(text: str, file_name: str) -> str:
    mode = 'w'
    if text.startswith('https://'):
        text = requests.get(text).content
        mode = 'wb'

    with open(file_name, mode) as f:
        f.write(text)

    return file_name


def copy_without_overwrite(src, dst):
    if os.path.exists(dst):
        return
    shutil.copy2(src, dst)

    return dst


def prepare_workdir(workdir: Path):
    """Create necessary directories if needed, such as templates directory, articles directory, etc.

    :param workdir: Working directory, where the blog is generated.
    :return: Working dir and Template dir Path objects
    """
    workdir.joinpath('articles').mkdir(exist_ok=True)

    templates_dir = workdir / 'templates'
    app_templates_dir = Path(__file__).parent.parent / 'templates'

    shutil.copytree(app_templates_dir, templates_dir, copy_function=copy_without_overwrite, dirs_exist_ok=True)

    return workdir, templates_dir


def get_md5_hash(text: str) -> str:
    return hashlib.md5(str(text).encode()).hexdigest()
