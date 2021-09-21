from abc import ABC, abstractmethod, ABCMeta

from ..exceptions import ProviderSettingsNotFound, BadProviderSettingsError
from ..registry import translation_provider_registry


class TranslateProviderMeta(ABCMeta):
    def __new__(mcs, name, bases, attrs):
        obj = super().__new__(mcs, name, bases, attrs)

        translation_provider_registry.register_provider(obj)

        return obj


class BaseTranslateProvider(ABC, metaclass=TranslateProviderMeta):
    settings_key = ''

    def __init__(self, *args, **kwargs):
        pass

    @property
    @abstractmethod
    def id(self) -> str:
        """Translate provider id."""

    @abstractmethod
    def translate(self, text: str, source_abbreviation: str, target_abbreviation: str) -> str:
        """Translate `text` into the given language."""

    @classmethod
    def from_settings(cls, settings):
        engine_settings = getattr(settings, cls.settings_key)
        try:
            return cls(**engine_settings)
        except TypeError:
            raise BadProviderSettingsError

    @abstractmethod
    def get_provider(self):
        pass
