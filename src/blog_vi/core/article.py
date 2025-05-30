from datetime import datetime, timezone
from functools import reduce
from pathlib import Path
from urllib.parse import urljoin

import markdown
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from jinja2 import FileSystemLoader, Environment
from slugify import slugify

from .tracker import Tracker

from .utils import get_md_file, ImgExtExtension, H1H2Extension


class Article:
    """Class representing an article in the blog."""
    base_template: str = 'article.html'

    def __init__(self, settings: 'Settings', title, timestamp, header_image, author_name, author_image, author_email,
                 summary, categories, markdown, author_info, author_social, status, slug, landing, is_legacy=False,
                 redirect_slug=None, previous=None, next=None, template=None, modified_timestamp=None):
        self.settings = settings
        self.landing = landing

        self.workdir = Path(self.landing.workdir, 'articles')
        self.templates_dir = settings.templates_dir

        # Article card data
        self.title = title
        self.header_image = header_image
        self.summary = summary
        self.categories = categories
        self.status = status
        self.timestamp = timestamp
        self.publish_date = self._get_publish_date()
        self.modified_timestamp = modified_timestamp or timestamp # Default to timestamp if None

        # Calculated fields
        self.wordCount = 0
        self.readingTime = 0 # In minutes

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
        self.slug = slugify(title) if not slug else slug

        self.redirect_slug = redirect_slug

        self.template = template or self.base_template

        self.url = self.prepare_url()

        self.is_legacy = is_legacy

        self.toc_html = ""

        self.tracker = Tracker(self, ['title', 'markdown', 'summary', 'categories', 'is_legacy'], self._get_output_dir())

    @property
    def path(self):
        output_dir = self._get_output_dir()
        relative_path = output_dir.relative_to(self.settings.workdir)
        return urljoin(self.settings.blog_root_path, str(relative_path))

    @classmethod
    def from_config(cls, settings: 'Settings', landing, config: dict) -> 'Article':
        """Return a class instance from the given config."""
        timestamp = datetime.strptime(config['Timestamp'], '%m/%d/%Y %H:%M:%S').replace(tzinfo=timezone.utc)

        # Handle optional modified timestamp
        modified_timestamp_str = config.get('Modified Timestamp')
        modified_timestamp = None
        if modified_timestamp_str:
            try:
                modified_timestamp = datetime.strptime(modified_timestamp_str, '%m/%d/%Y %H:%M:%S').replace(tzinfo=timezone.utc)
            except ValueError:
                # Handle potential parsing errors, e.g., log a warning or ignore
                print(f"Warning: Invalid 'Modified Timestamp' format for article '{config.get('Title')}'. Using original timestamp.")
                pass # Keep modified_timestamp as None, will default later

        return cls(
            settings,
            landing=landing,
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
            slug=config['Slug'],
            is_legacy=config.get('Is Legacy', False),
            redirect_slug=config.get('Redirect Slug'),
            timestamp=timestamp,
            modified_timestamp=modified_timestamp,
            markdown=config['Markdown'],
        )

    def generate(self):
        """Generate an article."""
        if not self.tracker.is_changed():
            return

        filepath = self._md_to_html()

        output_dir = self._get_output_dir()
        path_to_article = output_dir.relative_to(self.workdir)

        directory_loader = FileSystemLoader([ self.workdir, self.templates_dir.resolve()])
        env = Environment(loader=directory_loader)
        template = env.get_template(self.template)
        rendered = template.render(
            content=str(Path(path_to_article, 'index.html')),
            article=self,
            settings=self.settings,
            landing=self.landing
        )

        filepath.write_text(rendered)

    def _md_to_html(self) -> Path:
        """Convert markdown content to the html one and return the path to resulting file."""
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            # Revert permalink to True, will style with CSS
            TocExtension(permalink=True, toc_depth='2-2'),
            ImgExtExtension(),
            H1H2Extension(),
            TableExtension()
        ])
        source = self.workdir.joinpath(f'{self.slug}.md')

        output_dir = self._get_output_dir()
        output = output_dir.joinpath('index.html')

        md_file = get_md_file(self.markdown, str(source))

        # Calculate word count and reading time from the fetched markdown file
        try:
            with open(md_file, 'r', encoding='utf-8') as f: # Specify encoding
                content = f.read()
            self.wordCount = len(content.split())
            self.readingTime = max(1, round(self.wordCount / 200)) # Min 1 minute reading time
        except Exception as e:
            print(f"Warning: Could not calculate word count/reading time for {self.slug}: {e}")
            # Keep defaults (0)

        html_content = md.convert(content) # Convert content string instead of file to get TOC
        self.toc_html = md.toc # Store the generated TOC

        # Write the HTML content to the output file
        with open(output, 'w', encoding='utf-8') as f:
            f.write(html_content)

        source.unlink()

        return output

    def _get_publish_date(self) -> str:
        return self.timestamp.strftime('%B %d, %Y')

    def _get_output_dir(self) -> Path:
        output_dir = self.workdir.joinpath(self.slug)
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
        _url_bits = (self.settings.domain_url, self.path)
        url_bits = []
        for bit in _url_bits:
            if not bit.endswith('/'):
                bit += '/'

            if bit.startswith('/'):
                bit = bit[1:]

            url_bits.append(bit)

        return reduce(urljoin, url_bits)
