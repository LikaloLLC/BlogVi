import glob
from datetime import datetime

import markdown
from jinja2 import FileSystemLoader, Environment

from utils import get_data, ImgExtExtension, H1H2Extension


# https://docs.google.com/spreadsheets/d/1deKANndKOOmOdQUQWDK6-zC7P6J25SzBrUx2RX9lvkY/gviz/tq?tqx=out:csv&sheet=Form%20Responses%201


class Blog():

  def __init__(self, timestamp=None, header_image=None, author_name=None, author_image=None, author_email=None,
               summary=None, categories=None, markdown=None, detail_url=None,
               author_info=None, author_social=None, status=None):
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

  def generate_categories(self):
    pass

  def generate_landing_page(self):
    md = markdown.Markdown(extensions=[ImgExtExtension(), H1H2Extension()])
    directory_loader = FileSystemLoader('templates')

    env = Environment(loader=directory_loader)
    tm = env.get_template('base_index.html')

    for html_file in glob.glob('articles/*.html'):
      name = html_file
      name = name.replace("articles/", "")
      with open(html_file, 'r') as f:
        html_file = f.read()

      ms = tm.render(html_content=html_file)
      self.detail_url = f'templates/blogs/{name}'
      with open(f'templates/blogs/{name}', 'w') as f:
        f.write(ms)

    # header_image = file.images[0]
    # name_image = md.h1s

    directory_loader = FileSystemLoader('templates')
    env = Environment(loader=directory_loader)
    tm = env.get_template('base_landing.html')

    templates = []

    for file in glob.glob("templates/tailwind_g/includes/*.html"):
      file = file.replace("templates/", "")
      templates.append(file)

    ms = tm.render(templates=templates, blog=self)

    with open('templates/landing.html', 'w') as f:
      f.write(ms)

  def generate_articles(self):
    for md_file in glob.glob('articles/*.md'):
      md_file.replace("articles/", "")
      markdown.markdownFromFile(input=md_file, output=f'{md_file[:len(md_file) - 3]}.html')

  def generate_rss(self):
    pass

  def create_search_index(self):
    pass

  def create(self):
    directory_loader = FileSystemLoader('templates')
    env = Environment(loader=directory_loader)

    tm = env.get_template('blog_schema.html')
    name_file = (str(datetime.now()) + "|test").replace('.', '')
    ms = tm.render(blog=self, url=f"tailwind_g/includes/{name_file}.html")

    with open(f'templates/tailwind_g/includes/{name_file}.html', mode="w") as f:
      f.write(ms)


def main():
  url = "https://docs.google.com/spreadsheets/d/1deKANndKOOmOdQUQWDK6-zC7P6J25SzBrUx2RX9lvkY/gviz/tq?tqx=out:csv&sheet=Form%20Responses%201"
  datas = get_data(url)
  blog = Blog()
  blog.generate_articles()
  for data in datas:
    # if data['Status']:
    blog.author_name = data['Author Name']
    blog.markdown = data['Markdown']
    blog.author_image = data['Author Avatar Image URL']
    blog.categories = data['Categories ']
    blog.summary = data['Excerpt/Short Summary']
    blog.header_image = data['Header Image (will be used in RSS feed)']
    blog.author_info = data['About the Author']
    blog.timestamp = data['Timestamp']
    blog.detail_url = None
    blog.create()

  blog.generate_landing_page()


if __name__ == '__main__':
  main()
