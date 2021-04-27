import datetime
import glob
import json
import os

import markdown
import yaml
from feedgen.feed import FeedGenerator
from jinja2 import FileSystemLoader, Environment
from slugify import slugify

from utils import get_md_file, ImgExtExtension, H1H2Extension, get_data

# Philippe`s google Sheet
# https://docs.google.com/spreadsheets/d/1deKANndKOOmOdQUQWDK6-zC7P6J25SzBrUx2RX9lvkY/gviz/tq?tqx=out:csv&sheet=Form%20Responses%201

# Zarif`s google sheet
# "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNYmtcxqYplBu7SlY6grJRb3Y0vrmOBkE8j2CyeQlQHq4ElynBfi0Tkd4h2u2tPj4EmeGFBxyy8g73/pub?output=csv"

blogs_list = []
all_categories = set()


class Blog:
  def __init__(self, title=None, timestamp=None, header_image=None, author_name=None, author_image=None,
               author_email=None,
               summary=None, categories=None, markdown=None, detail_url=None,
               author_info=None, author_social=None, status=None) -> None:
    self.title = title
    self.author_name = author_name
    self.markdown = markdown
    self.header_image = header_image
    self.author_image = author_image
    self.author_email = author_email
    self.summary = summary
    self.timestamp = timestamp
    self.categories = categories
    self.author_info = author_info
    self.author_social = author_social
    self.status = status
    self.detail_url = detail_url

  def __str__(self) -> str:
    return f"Blog is about {self.author_name}"

  def all(self) -> dict:
    """
    return all attributes of the blog
    """
    dct = {
      'title': self.title,
      'author_name': self.author_name,
      'author_email': self.author_email,
      'author_info': self.author_info,
      'author_image': self.author_image,
      'author_social': self.author_social,
      'markdown': self.markdown,
      'header_image': self.header_image,
      'summary': self.summary,
      'timestamp': self.timestamp,
      'categories': self.categories,
      'status': self.status,
      'detail_url': self.detail_url
    }
    return dct

  def generate_categories(self):
    """
    Filtered data by tag
    """
    dct = dict()
    self.generate_landing_page()
    for tag in all_categories:
      dct[tag] = []

    for tag in dct:
      for blg in blogs_list:
        if tag[0] in blg.get('categories'):
          dct[tag].append(blg)

    for key, value in dct.items():
      self.generate_landing_page(key, value)

  def generate_landing_page(self, category=None, queryset=None) -> None:
    """
    Generate landing page for each category or index.html page
    category, queryset is optional
    """
    if queryset is None or category is None:
      queryset = blogs_list
      path_landing = 'templates/index.html'
    else:
      path_landing = f'templates/{category[1]}'

    try:
      directory_loader = FileSystemLoader('templates')
      env = Environment(loader=directory_loader)

      tm = env.get_template('base_landing.html')

      ms = tm.render(
        blogs=queryset,
        head_blog=queryset[len(queryset) - 1],
        categories=all_categories,
        searchConfig=self.create_search_index())
      with open(path_landing, 'w') as f:
        f.write(ms)

      # print(queryset)
      jns = json.dumps(blogs_list, indent=4)
      with open('templates/data.json', 'w') as jsonf:
        jsonf.write(jns)

    except Exception as e:
      print("Error", e)

  def generate_articles(self) -> None:
    """
    Convert md to html
    """
    md = markdown.Markdown(
      extensions=[ImgExtExtension(), H1H2Extension()])
    file_name = slugify(self.title)
    md_file = get_md_file(self.markdown, file_name)
    file_name = file_name.replace("templates/articles/", "")
    self.detail_url = f'{file_name}.html'
    blogs_list.append(self.all())

    md.convertFile(md_file, f'{md_file[:len(md_file) - 3]}.html')

    for file in glob.glob('templates/articles/*.md'):
      os.remove(file)
      # pass

  def create_blog(self) -> None:
    """
    Generate blog page for each markdown file.
    """
    directory_loader = FileSystemLoader('templates')
    env = Environment(loader=directory_loader)
    tm = env.get_template('base_blog.html')

    ms = tm.render(blog=f'articles/{self.detail_url}', head_blog=self)

    with open(f'templates/blogs/{self.detail_url}', mode="w") as f:
      f.write(ms)

    self.detail_url = f'templates/blogs/{self.detail_url}'
    self.generate_rss()

  def generate_rss(self):
    fg = FeedGenerator()
    fg.id("http://localhost:63342/BlogVi/templates/index.html")
    fg.title('Minimal Blog')
    # fg.author({'name': data.get('author_name'), 'email': data.get('author_email')})
    fg.link(href='http://localhost:63342/BlogVi/templates/index.html', rel='alternate')
    # fg.logo(data.get('author_image'))
    fg.subtitle("Minimaal BlogV RSS ")
    fg.language('en')
    for data in blogs_list:
      url = f'http://localhost:63342/BlogVi/templates/blogs/{data.get("detail_url")}'
      fe = fg.add_entry()
      fe.id(url)
      fe.title(data.get('author_name'))
      fe.summary(data.get('summary'))
      fe.link(href=url)
      fe.published()

    fg.rss_file('rss.xml')

  def create_search_index(self):
    with open('1_settings.yaml', 'r') as yml:
      x = json.dumps(yaml.safe_load(yml), indent=4)
      search_field_options = json.loads(x)
      options = dict()
      options['keys'] = []
      for field_name, field_options in search_field_options['keys'].items():
        options["keys"].append(
          {
            "name": field_name,
            **field_options
          }
        )
      return options


def main() -> None:
  # url = "https://docs.google.com/spreadsheets/d/1deKANndKOOmOdQUQWDK6-zC7P6J25SzBrUx2RX9lvkY/gviz/tq?tqx=out:csv&sheet=Form%20Responses%201"
  url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNYmtcxqYplBu7SlY6grJRb3Y0vrmOBkE8j2CyeQlQHq4ElynBfi0Tkd4h2u2tPj4EmeGFBxyy8g73/pub?output=csv"
  datas = get_data(url)
  blog = Blog()
  blog.create_search_index()
  for data in datas:
    if data['Status'] == '1':
      blog.title = data.get('title')
      blog.author_name = data['Author Name']
      blog.author_email = data['Author email']
      blog.author_info = data['About the Author']
      blog.author_image = data['Author Avatar Image URL']
      blog.author_social = data['linked.in github urls']
      blog.summary = data['Excerpt/Short Summary']
      blog.categories = [x for x in data['Categories '].split(", ")]
      blog.timestamp = data['Отметка времени']
      blog.status = 1
      # blog.timestamp = data['Timestamp'].replace("/", ".")
      blog.markdown = data['Markdown']
      blog.generate_articles()
      blog.create_blog()

      for tag in blog.categories:
        all_categories.add((tag, f"{slugify(tag)}-landing.html"))

      # print(blog.categories)
  blog.generate_categories()


if __name__ == '__main__':
  print("Running, Please wait")
  print(datetime.datetime.now())
  main()
  print(datetime.datetime.now())
  print("Succes, Please open the index.html in browser")
