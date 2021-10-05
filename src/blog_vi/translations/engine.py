from pathlib import Path

from blog_vi.__main__ import Landing, Article

from .exceptions import (
    BadProviderSettingsError,
    TranslateEngineNotFound
)
from .registry import translation_provider_registry


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
                translated_landing.add_article(self.translate_article(article, workdir, target_abbreviation))
            except Exception as e:
                print(f'[-] Something went wrong when translating article {article.title} - {e}')

        return translated_landing

    def translate_article(self, article: Article, workdir: Path, target_abbreviation: str) -> Article:
        """
        Translate article title, summary and text into the target language,
        specified by `target_abbreviation` param.
        """
        cloned_article = self.clone_article_for_translation(article, workdir)

        if not article.tracker.is_changed() and cloned_article.tracker.tracked_exists():
            tracked_data = cloned_article.tracker.get_tracked_data()

            cloned_article.title = tracked_data['title']['content']
            cloned_article.summary = tracked_data['summary']['content']
            cloned_article.markdown = tracked_data['markdown']['content']

            return cloned_article

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

        translated_categories = []
        for category in cloned_article.categories:
            translated_categories.append(self.translator.translate(
                text=category,
                source_abbreviation=self.source_abbreviation,
                target_abbreviation=target_abbreviation
            ))
        cloned_article.categories = translated_categories

        return cloned_article

    def clone_landing_for_translation(self, workdir: Path) -> Landing:
        return Landing(
            self.settings,
            self.landing.name,
            link_menu=self.landing.link_menu,
            search_config=self.landing.search_config,
            workdir=workdir,
            rootdir=self.landing.workdir
        )

    def clone_article_for_translation(self, article, workdir: Path) -> Article:
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

    def get_translation_workdir(self, folder_name: str) -> Path:
        workdir = Path(self.landing.workdir, folder_name)
        workdir.mkdir(exist_ok=True)

        return workdir
