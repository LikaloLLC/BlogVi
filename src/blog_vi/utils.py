import csv
import shutil
from pathlib import Path

import requests
import yaml
from markdown import Extension
from ._config import SETTINGS_FILENAME
from markdown.treeprocessors import Treeprocessor


class ImgExtractor(Treeprocessor):
    def run(self, doc):
        """Find all images and append to markdown.images."""
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


DEFAULTS = {
    'link_menu': [],
    'search_config': {
        'title': {
            'weight': 8
        },
        'summary': {
            'weight': 6
        },
        'author_name': {
            'weight': 5
        },
        'categories': {
            'weight': 3
        }
    },
    'comments': {
        'enabled': False,
    },
    'subscribe': {
        'enabled': False
    }
}


class Settings:
    mandatory = ('blog_name', 'landing_name', 'landing_description',
                 'landing_image', 'theme', 'template', 'blog_root_url', 'url')
    optional = DEFAULTS

    def __init__(self, workdir: Path, templates_dir: Path, **settings):
        self.workdir = workdir
        self.templates_dir = templates_dir

        self.fill_settings(settings)

    def fill_settings(self, settings):
        # Fill mandatory settings. May raise AttributeError
        self.__dict__.update({key: settings['mandatory'][key] for key in self.mandatory})

        # Fill optional settings
        if settings.get('optional') is not None:
            self.__dict__.update(
                {
                    key: settings['optional'].get(key, default)
                    for key, default in self.optional.items()}
            )

        # Fill other settings
        self.__dict__.update({key: value for key, value in settings.items() if key not in ['mandatory', 'optional']})


def make_json(file: str) -> list:
    data = []
    # read records from data.csv file and convert it list
    with open(file, encoding='utf-8') as f:
        csvReader = csv.DictReader(f)
        for rows in csvReader:
            data.append(rows)
    return data


def get_data(url: str) -> list:
    response = requests.get(url=url)
    # write records to data.csv file
    with open('data.csv', 'wb') as f:
        f.write(response.content)

    # with open('data.csv') as f:
    data = make_json('data.csv')
    return data


def get_md_file(text: str, file_name: str) -> None:
    mode = 'w'
    if text.startswith('https://'):
        text = requests.get(text).content
        mode = 'wb'

    with open(file_name, mode) as f:
        f.write(text)

    return file_name


def get_settings(filename: str = '1_settings.yaml') -> dict:
    """Return settings dictionary.

    :param filename: path to yaml settings file, defaults to `1_settings.yaml`
    :return: settings dictionary object
    :rtype: dict
    """

    return yaml.load(open(filename), Loader=yaml.FullLoader)


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

    return workdir, templates_dir
