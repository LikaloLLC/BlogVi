import json
import mimetypes
from itertools import zip_longest
from pathlib import Path
from typing import List, Dict
from urllib.parse import urljoin

from feedgen.feed import FeedGenerator
from jinja2 import FileSystemLoader, Environment
from slugify import slugify

from .article import Article


class BaseLanding:
    """A class representing a landing page for blog."""
    # Filename of the base template. Overrides with the `template` argument in __init__().
    base_template: str = 'blog.html'

    def __init__(
            self,
            settings: 'Settings',
            name: str,
            link_menu: dict = None,
            search_config: dict = None,
            template: str = None,
            workdir: Path = None
    ):
        self.settings = settings

        self.workdir = workdir or settings.workdir
        self.templates_dir = settings.templates_dir

        self.name = name
        self.link_menu = link_menu or {}
        self.search_config = search_config or {}

        self.template = template or self.base_template

        # List of included articles. Filled via `.add_article()` method.
        self._articles: List[Article] = []

        # List of categories. Filled from the articles categories automatically.
        self._categories: Dict[str, ''] = {}

    @property
    def path(self):
        """Return a path to this landing."""
        relative_path = str(self.workdir.relative_to(self.settings.workdir))
        if relative_path == '.':
            relative_path = ''

        path = urljoin(self.settings.blog_root_path, str(relative_path))
        if path.endswith('/'):
            path = path[:-1]

        return path

    @property
    def blog_path(self):
        """
        Return a path to a blog landing.
        This is useful e.g. for category landings to get the path to the parent landing.
        """
        raise NotImplementedError

    @classmethod
    def from_settings(cls, settings: 'Settings', **kwargs) -> 'Landing':
        """Return an instance from the given settings and automatically prepare neccessary parameters."""
        search_config = cls.prepare_search_config(settings.search_config)

        landing_kwargs = {'settings': settings, 'name': settings.blog_name,
                          'link_menu': settings.link_menu, 'search_config': search_config, **kwargs}

        return cls(**landing_kwargs)

    def get_articles(self) -> List['Article']:
        return self._articles.copy()

    def add_article(self, article: 'Article'):
        """Validate and add an article to the list of articles."""
        self._articles.append(article)

    def pre_generate_hook(self):
        pass

    def post_generate_hook(self):
        pass

    def generate(self, filename: str = 'index.html'):
        """Generate the landing page and its contents, such as articles and categories."""
        self.pre_generate_hook()

        rendered = self.render_template()

        filepath = self.workdir.joinpath(filename)
        filepath.write_text(rendered)

        self.post_generate_hook()

    def render_template(self):
        directory_loader = FileSystemLoader(self.templates_dir.resolve())
        env = Environment(loader=directory_loader)

        template = env.get_template(self.template)

        categories = {(category, f'{slugify(category)}/') for category in self._categories.keys()}
        head_article = self._articles[0] if self._articles else None

        return template.render(
            articles=self._articles[1:],
            head_article=head_article,
            categories=categories,
            searchConfig=self.search_config,
            settings=self.settings,
            blog=self
        )

    @staticmethod
    def prepare_search_config(search_config) -> dict:
        return {
            'keys': [
                {'name': field, **options}
                for field, options in search_config.items()
            ]
        }

    def cache_changes(self):
        """Create cache files for articles."""
        for article in self.get_articles():
            article.tracker.save_changes()


class Landing(BaseLanding):
    @property
    def blog_path(self):
        return self.path

    def generate_rss(self):
        domain = self.settings.domain_url
        blog_path = self.settings.blog_root_path
        fg = FeedGenerator()

        fg.id(f"{domain}{blog_path}index.html")
        fg.title(self.name)
        fg.link(href=f'{domain}{blog_path}index.html', rel='self')
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

        fg.rss_file(str(self.workdir / 'rss.xml'))

    def generate_articles(self) -> List['Article']:
        """A hook returning pregenerated articles, that are ready to be generated."""
        articles_to_generate = list(filter(lambda art: art.status == 1, self._articles))
        for current, next in zip_longest(
                articles_to_generate, articles_to_generate[1:], fillvalue=None
        ):
            if next:
                next.previous = {
                    'link': f'../{Path(current.path).name}',
                    'title': current.title
                }

                current.next = {
                    'link': f'../{Path(next.path).name}',
                    'title': next.title
                }

        for article in articles_to_generate:
            try:
                article.generate()
            except Exception as e:
                print(f'[!] Error generating article {article.title}: {e}')
                continue

        # Order articles in chronological order
        return sorted(articles_to_generate, key=lambda i: i.timestamp, reverse=True)

    def generate_categories(self) -> Dict[str, 'Landing']:
        """A hook returning pregenerated categories, that are ready to be generated."""
        category_landings = {}

        for article in self._articles:
            for category in article.categories:
                workdir = Path(self.workdir, slugify(category))
                workdir.mkdir(exist_ok=True)
                if not category:
                    continue
                category_landing = category_landings.get(category,
                                                         CategoryLanding.from_settings(self.settings,
                                                                                       workdir=workdir,
                                                                                       name=category))
                category_landing.add_article(article)
                category_landings[category] = category_landing

        return category_landings

    def pre_generate_hook(self):
        Path(self.workdir, 'articles').mkdir(exist_ok=True)

        # Generate categories only for the main landing page.
        self._articles = self.generate_articles()
        self._categories = self.generate_categories()

    def post_generate_hook(self):
        for category, landing in self._categories.items():
            landing.generate('index.html')

        # Used for search
        json.dump([article.to_dict() for article in self._articles], self.workdir.joinpath('data.json').open('w'))

        self.generate_rss()


class CategoryLanding(BaseLanding):
    @property
    def blog_path(self):
        """Return the path to parent directory, that is actually a blog."""
        current_relative_path = self.workdir.relative_to(self.settings.workdir)
        blog_relative_path = current_relative_path.parent

        if blog_relative_path == '.':
            blog_relative_path = ''

        path = urljoin(self.settings.blog_root_path, str(blog_relative_path))
        if path.endswith('/'):
            path = path[:-1]

        return path
