from .base import BaseTranslateProvider
import deepl


class DeeplTranslateProvider(BaseTranslateProvider):
    id = 'deepl'
    settings_key = 'deepl_translator'

    def __init__(self, api_key: str):
        self.__api_key = api_key

    def translate(self, text: str, source_abbreviation: str, target_abbreviation: str) -> str:
        provider = self.get_provider()
        result = provider.translate_text(text, source_lang=source_abbreviation, target_lang=target_abbreviation)
        text = result.text
        text = text.replace('] (', '](')

        return text

    def get_provider(self):
        return deepl.Translator(auth_key=self.__api_key)
