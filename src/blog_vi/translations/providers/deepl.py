from .base import BaseTranslateProvider
import deepl
from blog_vi._config import DEEPL_API_KEY


class DeeplTranslateProvider(BaseTranslateProvider):
    id = 'deepl'

    def translate(self, text: str, source_abbreviation: str, target_abbreviation: str) -> str:
        translator = deepl.Translator(DEEPL_API_KEY)
        result = translator.translate_text(text, source_lang=source_abbreviation, target_lang=target_abbreviation)

        return result.text
