import glob
import os
import random

import markdown
from jinja2 import FileSystemLoader, Environment

from utils import get_data, get_md_file, ImgExtExtension, H1H2Extension

# Philippe`s google Sheet
# https://docs.google.com/spreadsheets/d/1deKANndKOOmOdQUQWDK6-zC7P6J25SzBrUx2RX9lvkY/gviz/tq?tqx=out:csv&sheet=Form%20Responses%201

# Zarif`s google sheet
# "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNYmtcxqYplBu7SlY6grJRb3Y0vrmOBkE8j2CyeQlQHq4ElynBfi0Tkd4h2u2tPj4EmeGFBxyy8g73/pub?output=csv"

blogs_list = []


class Blog():

  def __init__(self, timestamp=None, header_image=None, author_name=None, author_image=None, author_email=None,
               summary=None, categories=None, markdown=None, detail_url=None,
               author_info=None, author_social=None, status=None) -> None:
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
    dct = {
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
    pass

  def generate_landing_page(self) -> None:
    md = markdown.Markdown(extensions=[ImgExtExtension(), H1H2Extension()])
    try:

      directory_loader = FileSystemLoader('templates')
      env = Environment(loader=directory_loader)
      tm = env.get_template('base_landing.html')

      n = random.randint(0, len(blogs_list))
      ms = tm.render(blogs=blogs_list, head_blog=blogs_list[n])
      # print(blogs_list)

      with open('templates/landing.html', 'w') as f:
        f.write(ms)
        print("Succes")
    except:
      raise Exception("Something went wrong")

  def generate_articles(self) -> None:
    file_name = self.author_name + self.timestamp
    md_file = get_md_file(self.markdown, file_name)
    file_name = file_name.replace("templates/articles/", "")
    self.detail_url = f'{file_name}.html'
    # print(self.detail_url)

    blogs_list.append(self.all())

    markdown.markdownFromFile(input=md_file, output=f'{md_file[:len(md_file) - 3]}.html')
    for file in glob.glob('templates/articles/*.md'):
      os.remove(file)

  def generate_rss(self):
    pass

  def create_search_index(self):
    pass

  def create_blog(self) -> None:
    directory_loader = FileSystemLoader('templates')
    env = Environment(loader=directory_loader)

    tm = env.get_template('base_index.html')

    ms = tm.render(blog=f'articles/{self.detail_url}')

    with open(f'templates/blogs/{self.detail_url}', mode="w") as f:
      f.write(ms)

    self.detail_url = f'templates/blogs/{self.detail_url}'
    # print(self.detail_url)


def main() -> None:
  # url = "https://docs.google.com/spreadsheets/d/1deKANndKOOmOdQUQWDK6-zC7P6J25SzBrUx2RX9lvkY/gviz/tq?tqx=out:csv&sheet=Form%20Responses%201"
  url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNYmtcxqYplBu7SlY6grJRb3Y0vrmOBkE8j2CyeQlQHq4ElynBfi0Tkd4h2u2tPj4EmeGFBxyy8g73/pub?output=csv"
  datas = get_data(url)
  blog = Blog()
  for data in datas:
    if data['Status']:
      blog.author_name = data['Author Name']
      blog.author_email = data['Author email']
      blog.author_info = data['About the Author']
      blog.author_image = data['Author Avatar Image URL']
      blog.author_social = data['linked.in github urls']
      blog.summary = data['Excerpt/Short Summary']
      blog.categories = data['Categories '].split(" ")
      blog.timestamp = data['Отметка времени']
      blog.markdown = data['Markdown']
      blog.generate_articles()
      blog.create_blog()
      print(blog.categories)
  blog.generate_landing_page()


if __name__ == '__main__':
  print("Running")
  main()
