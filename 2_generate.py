import glob

import markdown
from jinja2 import FileSystemLoader, Environment

from utils import get_data, get_md_file, ImgExtExtension, H1H2Extension

# Philippe`s google Sheet
# https://docs.google.com/spreadsheets/d/1deKANndKOOmOdQUQWDK6-zC7P6J25SzBrUx2RX9lvkY/gviz/tq?tqx=out:csv&sheet=Form%20Responses%201

# Zarif`s google sheet
# "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNYmtcxqYplBu7SlY6grJRb3Y0vrmOBkE8j2CyeQlQHq4ElynBfi0Tkd4h2u2tPj4EmeGFBxyy8g73/pub?output=csv"

blogs_list = []
all_categories = set()


class Blog:
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
    dct = dict()
    self.generate_landing_page()
    for category in all_categories:
      dct[category] = []
      # print(category)

    for item in dct:
      for blg in blogs_list:
        # print(blg)
        if item[0] in blg.get('categories'):
          dct[item].append(blg)

    for key, value in dct.items():
      self.generate_landing_page(key, value)

  def generate_landing_page(self, category=None, lst=None) -> None:
    # print(category, lst, '\n')
    if lst is None or category is None:
      lst = blogs_list
      path_landing = 'templates/index.html'

    else:
      path_landing = f"templates/{category[0]}_landing.html"
    try:
      directory_loader = FileSystemLoader('templates')
      env = Environment(loader=directory_loader)

      tm = env.get_template('base_landing.html')
      ms = tm.render(blogs=lst, head_blog=lst[len(lst) - 1], categories=all_categories)
      with open(path_landing, 'w') as f:
        f.write(ms)
        # print("Succes")
    except Exception as e:
      print("Error", e)

  def generate_articles(self) -> None:
    md = markdown.Markdown(
      extensions=[ImgExtExtension(), H1H2Extension()])
    file_name = self.author_name + self.timestamp
    md_file = get_md_file(self.markdown, file_name)
    file_name = file_name.replace("templates/articles/", "")
    self.detail_url = f'{file_name}.html'
    blogs_list.append(self.all())

    md.convertFile(md_file, f'{md_file[:len(md_file) - 3]}.html')

    for file in glob.glob('templates/articles/*.md'):
      # os.remove(file)
      pass

  def generate_rss(self):
    pass

  def create_search_index(self):
    pass

  def create_blog(self) -> None:
    directory_loader = FileSystemLoader('templates')
    env = Environment(loader=directory_loader)
    tm = env.get_template('base_index.html')

    ms = tm.render(blog=f'articles/{self.detail_url}', head_blog=self)

    with open(f'templates/blogs/{self.detail_url}', mode="w") as f:
      f.write(ms)

    self.detail_url = f'templates/blogs/{self.detail_url}'


def main() -> None:
  # url = "https://docs.google.com/spreadsheets/d/1deKANndKOOmOdQUQWDK6-zC7P6J25SzBrUx2RX9lvkY/gviz/tq?tqx=out:csv&sheet=Form%20Responses%201"
  url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNYmtcxqYplBu7SlY6grJRb3Y0vrmOBkE8j2CyeQlQHq4ElynBfi0Tkd4h2u2tPj4EmeGFBxyy8g73/pub?output=csv"
  datas = get_data(url)
  blog = Blog()
  for data in datas:
    if data['Status'] == '1':
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

      for item in blog.categories:
        all_categories.add((item, f"{item}_landing.html"))

      # print(blog.categories)
  blog.generate_categories()


if __name__ == '__main__':
  print("Running")
  main()
