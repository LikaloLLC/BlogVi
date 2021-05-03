import csv
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


def get_md_file(markdown_url: str, file_name: str) -> None:
  response = requests.get(markdown_url)

  articles_dir = Path(f"templates/articles/")
  articles_dir.mkdir(parents=True, exist_ok=True)

  file = articles_dir / f'{file_name}.md'
  file.write_bytes(response.content)

  return f"templates/articles/{file_name}.md"
