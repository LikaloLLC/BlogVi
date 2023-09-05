from pathlib import Path

from blog_vi.core.article import Article
from blog_vi.core.landing import Landing

from .exceptions import (
    BadProviderSettingsError,
    TranslateEngineNotFound
)
from .registry import translation_provider_registry
from blog_vi.core.utils import get_logger


class TranslateEngine:
    def __init__(self, landing: Landing, source_abbreviation: str):
        self.landing = landing
        self.source_abbreviation = source_abbreviation

        self.settings = landing.settings
        self.translator = self.get_translate_engine(self.settings)

        if self.translator is None:
            raise BadProviderSettingsError

    def get_translate_engine(self, settings):
        translator_cls = translation_provider_registry.get_provider(settings.translator)

        if translator_cls is None:
            raise TranslateEngineNotFound

        return translator_cls.from_settings(settings)

    def translate(self) -> None:
        """Translate landing and its articles into specified in the settings languages."""
        for translation in self.settings.translation_list:
            try:
                translated_landing = self.translate_landing(translation['abbreviation'])
                translated_landing.generate()
                translated_landing.cache_changes()
            except Exception as e:
                print(f'[-] Something went wrong when translating. Error - {e}')

    def translate_landing(self, target_abbreviation: str) -> Landing:
        """
        Translate landing and its articles into the target language,
        specified by `target_abbreviation` param.
        """
        workdir = self.get_translation_workdir(target_abbreviation)

        translated_landing = self.clone_landing_for_translation(workdir)

        for article in self.landing._articles:
            try:
                translated_landing.add_article(self.translate_article(article, translated_landing, target_abbreviation))
            except Exception as e:
                print(f'[-] Something went wrong when translating article {article.title} - {e}')

        return translated_landing

    def translate_article(self, article: Article, landing, target_abbreviation: str) -> Article:
        """
        Translate article title, summary and text into the target language,
        specified by `target_abbreviation` param.
        """
        logger = get_logger()
        cloned_article = self.clone_article_for_translation(article, landing)

        if not article.tracker.is_changed() and cloned_article.tracker.tracked_exists():
            tracked_data = cloned_article.tracker.get_tracked_data()

            cloned_article.title = tracked_data['title']['content']
            cloned_article.summary = tracked_data['summary']['content']
            cloned_article.markdown = tracked_data['markdown']['content']
            logger.info("Article from cache %r", cloned_article.title)
            return cloned_article

        title = cloned_article.title
        summary = cloned_article.summary
        markdown = cloned_article.markdown
        if title:
            cloned_article.title = self.translator.translate(
                text=title,
                source_abbreviation=self.source_abbreviation,
                target_abbreviation=target_abbreviation
            )
            logger.info("Article %r. Translate Article title from %r to %r", cloned_article.title,
                        self.source_abbreviation, target_abbreviation)
        if summary:
            cloned_article.summary = self.translator.translate(
                text=summary,
                source_abbreviation=self.source_abbreviation,
                target_abbreviation=target_abbreviation
            )
            logger.info("Article %r. Translate Article summary from %r to %r", cloned_article.title,
                        self.source_abbreviation, target_abbreviation)
        if markdown:
            cloned_article.markdown = self.translator.translate(
                text=markdown,
                source_abbreviation=self.source_abbreviation,
                target_abbreviation=target_abbreviation
            )
            logger.info("Article %r. Translate Article markdown from %r to %r", cloned_article.title,
                        self.source_abbreviation, target_abbreviation)

        translated_categories = []
        for category in cloned_article.categories:
            if category:
                category = self.translator.translate(
                    text=category,
                    source_abbreviation=self.source_abbreviation,
                    target_abbreviation=target_abbreviation
                )
                logger.info("Category %r. Translate Article markdown from %r to %r", category,
                            self.source_abbreviation, target_abbreviation)

            translated_categories.append(category)

        cloned_article.categories = translated_categories

        return cloned_article

    def clone_landing_for_translation(self, workdir: Path) -> Landing:
        return Landing(
            self.settings,
            self.landing.name,
            link_menu=self.landing.link_menu,
            search_config=self.landing.search_config,
            workdir=workdir
        )

    def clone_article_for_translation(self, article, landing) -> Article:
        return Article(
            self.settings,
            landing=landing,
            title=article.title,
            author_name=article.author_name,
            author_email=article.author_email,
            author_info=article.author_info,
            author_image=article.author_image,
            author_social=article.author_social,
            header_image=article.header_image,
            summary=article.summary,
            categories=article.categories,
            status=int(article.status),
            timestamp=article.timestamp,
            markdown=article.markdown,
            slug=article.slug
        )

    def get_translation_workdir(self, folder_name: str) -> Path:
        workdir = Path(self.landing.workdir, folder_name)
        workdir.mkdir(exist_ok=True)

        return workdir
