import json
import mimetypes
import sys
from datetime import datetime, timezone
from functools import reduce
from pathlib import Path
from typing import List, Dict
from urllib.parse import urljoin

import markdown
from feedgen.feed import FeedGenerator
from jinja2 import FileSystemLoader, Environment
from slugify import slugify

from ._config import SETTINGS_FILENAME
from ._settings import Settings, get_settings
from .tracker import Tracker
from .translations.exceptions import ProviderSettingsNotFound, TranslateEngineNotFound, BadProviderSettingsError
from .utils import get_md_file, ImgExtExtension, H1H2Extension, get_articles_from_csv, prepare_workdir


class Landing:
    """A class representing a landing page for blog.

    Can be used as an index page and as a category page.
    """
    # Filename of the base template. Overrides with the `template` argument in __init__().
    base_template: str = 'blog.html'

    def __init__(
            self,
            settings: 'Settings',
            name: str,
            link_menu: dict = None,
            search_config: dict = None,
            template: str = None,
            workdir: str = None,
            rootdir: str = None
    ):
        self.settings = settings

        self.workdir = workdir or settings.workdir
        self.blog_root_dir = rootdir or self.workdir

        self.templates_dir = settings.templates_dir

        self.root_url = urljoin(str(settings.blog_root), str(self.blog_root_dir))

        self.name = name
        self.link_menu = link_menu or {}
        self.search_config = search_config or {}

        self.template = template or self.base_template

        # List of included articles. Filled via `.add_article()` method.
        self._articles: List[Article] = []

        # List of categories. Filled from the articles categories automatically.
        self._categories: Dict[str, 'Landing'] = {}

    @classmethod
    def from_settings(cls, settings: 'Settings', **kwargs) -> 'Landing':
        """Return an instance from the given settings and automatically prepare neccessary parameters."""
        search_config = cls.prepare_search_config(settings.search_config)

        landing_kwargs = {'settings': settings, 'name': settings.blog_name,
                          'link_menu': settings.link_menu, 'search_config': search_config, **kwargs}

        return cls(**landing_kwargs)

    def get_articles(self) -> List['Article']:
        return self._articles.copy()

    def generate_rss(self):
        domain_url = self.settings.domain_url
        fg = FeedGenerator()

        fg.id(f"{domain_url}/index.html")
        fg.title(self.name)
        fg.link(href=f'{domain_url}/index.html', rel='self')
        fg.subtitle(self.name)
        fg.language('en')

        for article in self._articles:
            fe = fg.add_entry(order='append')

            fe.id(article.url)
            fe.title(article.title)
            fe.summary(article.summary)
            fe.link(href=article.url)
            fe.author(name=article.author_name, email=article.author_email)
            fe.category(category=[{'term': category} for category in article.categories])
            fe.enclosure(url=article.header_image, type=mimetypes.guess_type(article.header_image)[0] or '')
            fe.published(article.timestamp)

        fg.rss_file(str(self.blog_root_dir / 'rss.xml'))

    def add_article(self, article: 'Article'):
        """Validate and add an article to the list of articles."""
        self._articles.append(article)

    def pregenerate_categories(self) -> Dict[str, 'Landing']:
        """A hook returning pregenerated categories, that are ready to be generated."""
        category_landings = {}

        for article in self._articles:
            for category in article.categories:
                workdir = Path(self.workdir, slugify(category))
                workdir.mkdir(exist_ok=True)

                category_landing = category_landings.get(category,
                                                         Landing.from_settings(self.settings,
                                                                               workdir=workdir,
                                                                               rootdir=self.workdir,
                                                                               name=category))
                category_landing.add_article(article)
                category_landings[category] = category_landing

        return category_landings

    def pregenerate_articles(self) -> List['Article']:
        """A hook returning pregenerated articles, that are ready to be generated."""
        generated_articles = []

        for article in self._articles:
            if article.status != 1:
                continue

            # Generates previous and next links for each article
            if generated_articles:
                article.previous = {
                    'link': f'../{Path(generated_articles[-1].path).name}',
                    'title': generated_articles[-1].title
                }

                generated_articles[-1].next = {
                    'link': f'../{Path(article.path).name}',
                    'title': article.title
                }

            try:
                article.generate()
            except Exception as e:
                print(f'[!] Error generating article {article.title}: {e}')
                continue

            generated_articles.append(article)

        # Order articles in chronological order
        return sorted(generated_articles, key=lambda i: i.timestamp, reverse=True)

    def generate(self, filename: str = 'index.html', is_category: bool = False):
        """Generate the landing page and its contents, such as articles and categories."""
        if not is_category:
            Path(f"{self.workdir}/articles").mkdir(exist_ok=True)

        # Generate categories only for the main landing page.
        if not is_category:
            self._articles = self.pregenerate_articles()
            self._categories = self.pregenerate_categories()

        directory_loader = FileSystemLoader(self.templates_dir)
        env = Environment(loader=directory_loader)

        template = env.get_template(self.template)

        template_categories = {(category, f'{slugify(category)}/') for category in self._categories.keys()}
        head_article = self._articles[0] if self._articles else None

        rendered = template.render(
            articles=self._articles[1:],
            head_article=head_article,
            categories=template_categories,
            searchConfig=self.search_config,
            settings=self.settings,
            blog=self
        )

        for category, landing in self._categories.items():
            # `is_category` MUST always be set to True, when generating non-index pages.
            landing.generate('index.html', is_category=True)

        filepath = self.workdir.joinpath(filename)
        filepath.write_text(rendered)

        if not is_category:
            json.dump([article.to_dict() for article in self._articles], self.workdir.joinpath('data.json').open('w'))

            self.generate_rss()

    @staticmethod
    def prepare_search_config(search_config) -> dict:
        return {
            'keys': [
                {'name': field, **options}
                for field, options in search_config.items()
            ]
        }


class Article:
    """Class representing an article in the blog."""
    base_template: str = 'article.html'

    def __init__(self, settings: 'Settings', title, timestamp, header_image, author_name, author_image, author_email,
                 summary, categories, markdown, author_info, author_social, status, previous=None, next=None,
                 template=None, workdir=None):
        self.settings = settings

        self.workdir = workdir or settings.workdir
        self.templates_dir = settings.templates_dir

        # Article card data
        self.title = title
        self.header_image = header_image
        self.summary = summary
        self.categories = categories
        self.status = status
        self.timestamp = timestamp
        self.publish_date = self._get_publish_date()

        # Source markdown file url
        self.markdown = markdown

        # Author data
        self.author_name = author_name
        self.author_image = author_image
        self.author_email = author_email
        self.author_info = author_info
        self.author_social = author_social

        # Previous and next article links
        self.previous = previous or {}
        self.next = next or {}

        # Misc
        self.slug = slugify(title)
        self.path = str(Path('articles', self.slug))
        self.root_path = str((self.settings.blog_root, 'articles', self.slug))
        self.template = template or self.base_template

        self.url = self.prepare_url()

        self.tracker = Tracker(self, ['title', 'markdown', 'summary', 'categories'], self._get_output_dir())

    @classmethod
    def from_config(cls, settings: 'Settings', config: dict) -> 'Article':
        """Return a class instance from the given config."""
        return cls(
            settings,
            title=config.get('Title'),
            author_name=config['Author Name'],
            author_email=config['Author email'],
            author_info=config['About the Author'],
            author_image=config['Author Avatar Image URL'],
            author_social=config['linked.in github urls'],
            header_image=config.get('Header Image (will be used in RSS feed)'),
            summary=config['Excerpt/Short Summary'],
            categories=config['Categories'].split(", "),
            status=int(config['Status']),
            timestamp=datetime.strptime(config['Timestamp'], '%m/%d/%Y %H:%M:%S').replace(tzinfo=timezone.utc),
            markdown=config['Markdown'],
        )

    def generate(self):
        """Generate an article."""
        if not self.tracker.is_changed():
            return

        filepath = self._md_to_html()

        directory_loader = FileSystemLoader([self.workdir, self.templates_dir])
        env = Environment(loader=directory_loader)
        template = env.get_template(self.template)
        rendered = template.render(
            blog=f'{self.path}/index.html',
            head_blog=self,
            settings=self.settings
        )

        filepath.write_text(rendered)

    def _md_to_html(self) -> Path:
        """Convert markdown content to the html one and return the path to resulting file."""
        md = markdown.Markdown(extensions=[ImgExtExtension(), H1H2Extension()])
        source = self.workdir.joinpath('articles', f'{self.slug}.md')

        output_dir = self._get_output_dir()
        output = output_dir.joinpath('index.html')

        md_file = get_md_file(self.markdown, str(source))
        md.convertFile(md_file, str(output))

        source.unlink()

        return output

    def _get_publish_date(self) -> str:
        return self.timestamp.strftime('%B %d, %Y')

    def _get_output_dir(self) -> Path:
        output_dir = self.workdir.joinpath('articles', self.slug)
        output_dir.mkdir(exist_ok=True, parents=True)

        return output_dir

    def to_dict(self) -> dict:
        keys = ('title', 'author_name', 'author_email', 'author_info', 'author_image', 'author_social', 'markdown',
                'header_image', 'summary', 'publish_date', 'categories', 'status', 'path', 'slug', 'previous',
                'next')

        return {key: getattr(self, key) for key in keys}

    def prepare_url(self):
        """
        Returns URL for the article. Takes domain url, blog directory from settings
        and concatenates it with relative article path."""
        _url_bits = (self.settings.domain_url, self.settings.blog_root_url, self.path)
        url_bits = []
        for bit in _url_bits:
            if not bit.endswith('/'):
                bit += '/'

            if bit.startswith('/'):
                bit = bit[1:]

            url_bits.append(bit)

        return reduce(urljoin, url_bits)


def generate_blog(workdir: Path) -> None:
    from .translations.engine import TranslateEngine

    workdir, templates_dir = prepare_workdir(workdir)

    settings_dict = get_settings(workdir / SETTINGS_FILENAME)
    settings = Settings(workdir, templates_dir, **settings_dict)

    url = settings.blog_post_location_url
    articles = get_articles_from_csv(url)

    index = Landing.from_settings(settings)

    for cnt, article in enumerate(articles):
        if article['Status'] != '1':
            continue

        article['Title'] = article.get('Title') or f'blog-{cnt}'

        article_obj = Article.from_config(settings, article)
        index.add_article(article_obj)

    index.generate()

    if settings.translate_articles:
        try:
            if settings.source_language is None:
                print('[-] Please, provide a source language abbreviation.')
                sys.exit(1)
            engine = TranslateEngine(index, settings.source_language['abbreviation'])
        except ProviderSettingsNotFound:
            print(f'[-] Settings not found for translate provider {settings.translator}')
        except TranslateEngineNotFound:
            print('[-] Translate engine not found')
        except BadProviderSettingsError:
            print(f'[-] Please, fill all {settings.translator} provider settings')
        except TypeError:
            print('[-] Please define translator provider in settings')
        else:
            engine.translate()

    for article in index.get_articles():
        article.tracker.save_changes()
