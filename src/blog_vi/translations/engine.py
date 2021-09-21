from pathlib import Path

from .exceptions import (
    BadProviderSettingsError,
    TranslateEngineNotFound
)
from .registry import translation_provider_registry
from blog_vi.__main__ import Landing, Article


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
        for target_abbreviation in self.settings.translation_list:
            try:
                translated_landing = self.translate_landing(target_abbreviation)
                translated_landing.generate()
            except Exception as e:
                print(f'[-] Something went wrong when translating. Error - {e}')

    def translate_landing(self, target_abbreviation: str) -> Landing:
        """
        Translate landing and its articles into the target language,
        specified by `target_abbreviation` param.
        """
        translated_landing = self.clone_landing_for_translation(target_abbreviation)

        for article in self.landing._articles:
            try:
                translated_landing.add_article(self.translate_article(article, target_abbreviation))
            except Exception as e:
                print(f'[-] Something went wrong when translating article {article.title} - {e}')

        return translated_landing

    def translate_article(self, article: Article, target_abbreviation: str) -> Article:
        """
        Translate article title, summary and text into the target language,
        specified by `target_abbreviation` param.
        """

        cloned_article = self.clone_article_for_translation(article, target_abbreviation)

        cloned_article.title = self.translator.translate(
            text=cloned_article.title,
            source_abbreviation=self.source_abbreviation,
            target_abbreviation=target_abbreviation
        )
        cloned_article.summary = self.translator.translate(
            text=cloned_article.summary,
            source_abbreviation=self.source_abbreviation,
            target_abbreviation=target_abbreviation
        )

        cloned_article.markdown = self.translator.translate(
            text=cloned_article.markdown,
            source_abbreviation=self.source_abbreviation,
            target_abbreviation=target_abbreviation
        )

        return cloned_article

    def clone_landing_for_translation(self, folder_name: str) -> Landing:
        workdir = Path(f'{self.landing.workdir}/{folder_name}')
        workdir.mkdir(exist_ok=True)

        return Landing(
            self.settings,
            self.landing.name,
            link_menu=self.landing.link_menu,
            search_config=self.landing.search_config,
            workdir=workdir
        )

    def clone_article_for_translation(self, article, folder_name: str) -> Article:
        workdir = Path(f'{self.landing.workdir}/{folder_name}')
        workdir.mkdir(exist_ok=True)
        return Article(
            self.settings,
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
            workdir=workdir
        )
