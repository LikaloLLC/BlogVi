import json
from datetime import datetime
from pathlib import Path

import markdown
import yaml
from feedgen.feed import FeedGenerator
from jinja2 import FileSystemLoader, Environment
from slugify import slugify

from ._config import SETTINGS_FILENAME
from .utils import get_md_file, ImgExtExtension, H1H2Extension, get_data, get_settings, prepare_workdir

# Philippe`s google Sheet
# https://docs.google.com/spreadsheets/d/1deKANndKOOmOdQUQWDK6-zC7P6J25SzBrUx2RX9lvkY/gviz/tq?tqx=out:csv&sheet=Form%20Responses%201

# Zarif`s google sheet
# "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNYmtcxqYplBu7SlY6grJRb3Y0vrmOBkE8j2CyeQlQHq4ElynBfi0Tkd4h2u2tPj4EmeGFBxyy8g73/pub?output=csv"

blogs_list = []
all_categories = set()


class Blog:
    def __init__(self, workdir: Path, templates_dir: Path, title=None, timestamp=None, header_image=None,
                 author_name=None,
                 author_image=None, author_email=None,
                 summary=None, categories=None, markdown=None, detail_url=None,
                 author_info=None, author_social=None, status=None, prev_link=None, next_link=None) -> None:
        self.workdir = workdir
        self.templates_dir = templates_dir

        self.title = title
        self.author_name = author_name
        self.markdown = markdown
        self.header_image = header_image
        self.author_image = author_image
        self.author_email = author_email
        self.summary = summary
        self.categories = categories
        self.author_info = author_info
        self.author_social = author_social
        self.status = status
        self.detail_url = detail_url
        self.prev_link = prev_link
        self.next_link = next_link

        self.publish_date = self.get_publish_date(timestamp) if timestamp else None

    def __str__(self) -> str:
        return f"Blog is about {self.author_name}"

    def all(self) -> dict:
        """Return all attributes of the blog."""
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
            'publish_date': self.publish_date,
            'categories': self.categories,
            'status': self.status,
            'detail_url': self.detail_url,
            'prev_link': self.prev_link,
            'next_link': self.next_link
        }
        return dct

    def generate_categories(self):
        """Filtered data by tag."""
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
            landing_index_path = self.workdir.joinpath('index.html')
        else:
            landing_index_path = self.workdir.joinpath(category[1])

        try:
            directory_loader = FileSystemLoader(self.templates_dir)
            env = Environment(loader=directory_loader)

            tm = env.get_template('base_landing.html')
            settings = get_settings(self.workdir / SETTINGS_FILENAME)
            ms = tm.render(
                blogs=queryset,
                head_blog=queryset[len(queryset) - 1],
                categories=all_categories,
                searchConfig=self.create_search_index(),
                settings=settings
            )

            landing_index_path.write_text(ms)

            json.dump(blogs_list, self.workdir.joinpath('data.json').open('w'))

        except Exception as e:
            print("Error", e)

    def generate_articles(self) -> None:
        """Convert md to html"""
        md = markdown.Markdown(extensions=[ImgExtExtension(), H1H2Extension()])
        file_name = slugify(self.title)
        filepath = self.workdir.joinpath('articles', f'{file_name}.md')

        md_file = get_md_file(self.markdown, str(filepath))

        self.detail_url = f'{file_name}.html'
        blogs_list.append(self.all())

        md.convertFile(md_file, f'{md_file[:len(md_file) - 3]}.html')

        for file in self.workdir.joinpath('articles').glob('*.md'):
            file.unlink()

    def create_blog(self) -> None:
        """Generate blog page for each markdown file."""
        directory_loader = FileSystemLoader([self.workdir, self.templates_dir])
        env = Environment(loader=directory_loader)
        tm = env.get_template('base_blog.html')
        settings = get_settings(self.workdir / SETTINGS_FILENAME)
        ms = tm.render(
            blog=str(Path('articles', self.detail_url)),
            head_blog=self,
            settings=settings
        )

        blogs_dir = self.workdir / 'blogs'
        blogs_dir.mkdir(parents=True, exist_ok=True)

        blogs_dir.joinpath(self.detail_url).write_text(ms)

        self.detail_url = str(blogs_dir / self.detail_url)
        self.generate_rss()

    def generate_rss(self):
        settings = get_settings(self.workdir / SETTINGS_FILENAME)
        domain_name = settings['optional']['link_menu']['link_1']
        template_path = "blog_vi/templates"
        fg = FeedGenerator()
        fg.id(f"{domain_name}/{template_path}/index.html")
        fg.title(settings['mandatory']['blog_name'])
        fg.link(href=f'{domain_name}/{template_path}/index.html', rel='alternate')
        fg.subtitle(settings['mandatory']['blog_name'])
        fg.language('en')
        for data in blogs_list:
            url = f'{domain_name}/{template_path}/blogs/{data.get("detail_url")}'
            fe = fg.add_entry()
            fe.id(url)
            fe.title(data.get('author_name'))
            fe.summary(data.get('summary'))
            fe.link(href=url)
            fe.published()

        fg.rss_file('rss.xml')

    def create_search_index(self):
        with self.workdir.joinpath(SETTINGS_FILENAME).open() as yml:
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

    def get_publish_date(self, timestamp: datetime) -> str:
        return timestamp.strftime('%B %d, %Y')


def generate_blog(workdir: Path) -> None:
    workdir, templates_dir = prepare_workdir(workdir)

    settings = get_settings(workdir / SETTINGS_FILENAME)

    url = settings['mandatory']['url']

    datas = get_data(url)
    blog = Blog(workdir, templates_dir)
    blog.create_search_index()
    cnt = 0
    for data in datas:
        if data['Status'] == '1':
            if data.get('Title'):
                blog.title = data.get('Title')
            else:
                blog.title = f'blog-{cnt}'
            blog.author_name = data['Author Name']
            blog.author_email = data['Author email']
            blog.author_info = data['About the Author']
            blog.author_image = data['Author Avatar Image URL']
            blog.author_social = data['linked.in github urls']
            blog.header_image = data.get('Header Image (will be used in RSS feed)')
            blog.summary = data['Excerpt/Short Summary']
            blog.categories = [x for x in data['Categories '].split(", ")]
            blog.status = 1
            blog.timestamp = data['Timestamp']
            blog.publish_date = blog.get_publish_date(datetime.strptime(data['Timestamp'], '%d/%m/%Y %H:%M:%S'))
            blog.markdown = data['Markdown']
            blog.generate_articles()
            current_link = slugify(blog.title) + '.html'

            try:
                if datas[cnt - 1].get('Title'):
                    if current_link != blog.prev_link:
                        blog.prev_link = slugify(datas[cnt - 1].get('Title')) + '.html'
                else:
                    if current_link != blog.prev_link:
                        blog.prev_link = slugify(f'blog-{cnt - 1}') + '.html'

                if cnt == len(datas) - 1:
                    cnt = -1

                if datas[cnt + 1].get('Title'):
                    if current_link != blog.prev_link:
                        blog.next_link = slugify(datas[cnt + 1].get('Title')) + '.html'
                else:
                    if current_link != blog.prev_link:
                        blog.next_link = slugify(f'blog-{cnt + 1}') + '.html'
            except Exception as e:
                pass
            blog.create_blog()
            for tag in blog.categories:
                all_categories.add((tag, f"{slugify(tag)}-landing.html"))

            cnt += 1
        for tag in blog.categories:
            all_categories.add((tag, f"{slugify(tag)}-landing.html"))

    blog.generate_categories()
