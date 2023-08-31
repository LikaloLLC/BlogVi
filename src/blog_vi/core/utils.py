import csv
import hashlib
import logging
import os
import shutil
from pathlib import Path

import requests
from markdown import Extension
from markdown.treeprocessors import Treeprocessor


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


def get_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s:%(asctime)s:%(message)s',
        handlers=[
            logging.FileHandler('blogvi.log'),  # Write logs to a file
            logging.StreamHandler()  # Display logs on the console
        ]
    )
    return logging
