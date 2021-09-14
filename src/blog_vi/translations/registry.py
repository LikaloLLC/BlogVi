from typing import Dict, Type

from .exceptions import TranslateEngineNotFound


class TranslationProviderRegistry:
    _registry: Dict[str, Type['BaseTranslateProvider']] = {}

    def register_provider(self, provider: Type['BaseTranslateProvider']) -> None:
        self._registry[provider.id] = provider

    def get_provider(self, id_: str) -> Type['BaseTranslateProvider']:
        try:
            return self._registry[id_]
        except KeyError:
            raise TranslateEngineNotFound

    def get_registry(self) -> Dict[str, Type['BaseTranslateProvider']]:
        return self._registry.copy()


translation_provider_registry = TranslationProviderRegistry()
