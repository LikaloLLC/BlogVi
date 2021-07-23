import csv
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


def prepare_workdir(workdir: Path):
    """Create necessary directories if needed, such as templates directiry, articles directory, etc.

    :param workdir: Working directory, where the blog is generated.
    :return: Working dir and Template dir Path objects
    """
    workdir.joinpath('articles').mkdir(exist_ok=True)

    templates_dir = workdir / 'templates'
    if not templates_dir.exists():
        app_templates_dir = Path(__file__).parent / 'templates'

        # Move the default template dir to the current workdir
        shutil.copytree(app_templates_dir, templates_dir)
    else:
        """Walk through the base templates directory and move missing templates to the user's templates dir."""

    return workdir, templates_dir
