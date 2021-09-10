from blog_vi.__main__ import Landing, Article


class TranslateEngine:
    def __init__(self, landing: Landing, source_abbreviation: str):
        self.landing = landing
        self.source_abbreviation = source_abbreviation

        self.settings = landing.settings

        # TODO:
        #   - Validate settings
        #   - Get translate provider from registry

    def translate(self) -> None:
        """Translate landing and its articles into specified in the settings languages."""
        for target_abbreviation in self.settings.translate_list:
            translated_landing = self.translate_landing(target_abbreviation)
            translated_landing.generate()

    def translate_landing(self, target_abbreviation: str) -> Landing:
        """
        Translate landing and its articles into the target language,
        specified by `target_abbreviation` param.
        """
        translated_landing = self.clone_landing_for_translation()

        for article in self.landing._articles:
            # TODO:
            #   - Translate article by calling `self.translate_article` for each existing article
            #   - Add translated article to the `translated_landing`
            pass

    def translate_article(self, article: Article, target_abbreviation: str) -> Article:
        """
        Translate article title, summary and text into the target language,
        specified by `target_abbreviation` param.
        """

    def clone_landing_for_translation(self, folder_name: str) -> Landing:
        workdir = self.landing.workdir / folder_name

        return Landing(
            self.settings,
            self.landing.name,
            link_menu=self.landing.link_menu,
            search_config=self.landing.search_config,
            workdir=workdir
        )
