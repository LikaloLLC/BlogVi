class TranslateError(Exception):
    """Base exception."""
    default_message: str = 'Translate error.'

    def __init__(self, message: str = None, *args):
        self.message = message or self.get_message()

        super().__init__(message, *args)

    def __str__(self):
        return self.message

    def get_message(self) -> str:
        return self.default_message


class TranslateEngineNotFound(TranslateError):
    """Translate provider not found"""

    def get_message(self) -> str:
        from .registry import translation_provider_registry

        return (f'Translate provider not found.'
                f' Possible engines are: {",".join(translation_provider_registry.get_registry().keys())}')


# More exceptions, derived from `TranslateError`, here...
class ProviderError(Exception):
    """Base exception."""
    default_message: str = 'Provider error.'

    def __init__(self, message: str = None, *args):
        self.message = message or self.get_message()

        super().__init__(message, *args)

    def __str__(self):
        return self.message

    def get_message(self) -> str:
        return self.default_message


class ProviderSettingsNotFound(ProviderError):
    default_message = "Provider settings not found"


class BadProviderSettingsError(ProviderError):
    default_message = "Provider settings filled incorrect"
