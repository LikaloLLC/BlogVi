# src/blog_vi/core/translations/providers/claude.py
import os
import anthropic
from typing import Optional
import logging

from .base import BaseTranslateProvider
from ..exceptions import TranslateError

logger = logging.getLogger(__name__)

class ClaudeTranslateProvider(BaseTranslateProvider):
    """
    Translation provider using the Anthropic Claude API.
    Uses Claude 3.7 Sonnet which has a 200K token context window and 128K output tokens with beta header.
    """
    id = 'claude'
    settings_key = 'claude_translator'
    
    def __init__(self, api_key: str, model: str = "claude-3-7-sonnet-20250219"):
        self.__api_key = api_key
        self.__model = model
        self.__client = None

    def translate(self, text: str, source_abbreviation: str, target_abbreviation: str) -> str:
        """
        Translate text using Claude 3.7 Sonnet API with 128K output tokens.
        No chunking needed due to large context window (200K tokens).
        """
        client = self.get_provider()
        
        # System message to set the context and requirements
        system_message = f"""You are a professional translator specializing in technical and blog content translation.
        Your task is to translate content from {source_abbreviation} to {target_abbreviation} while:
        1. Preserving all markdown formatting, links, and special characters exactly as they appear
        2. Only translating the actual text content, not markdown syntax or URLs
        3. Maintaining the original structure and formatting
        4. Ensuring technical terms are translated accurately
        5. Preserving code blocks and their content
        6. Maintaining proper spacing and line breaks
        
        Respond with ONLY the translated text, maintaining all original formatting."""
        
        try:
            # Create a streaming response with beta header for 128K output tokens
            with client.messages.stream(
                model=self.__model,
                max_tokens=128000,  # Maximum output tokens with beta header
                system=system_message,
                messages=[
                    {"role": "user", "content": f"Please translate the following text while preserving all formatting:\n\n{text}"}
                ],
                extra_headers={
                    "anthropic-beta": "output-128k-2025-02-19"  # Enable 128K output tokens
                }
            ) as stream:
                translated_text = []
                for text in stream.text_stream:
                    translated_text.append(text)
                
                # Join the streamed text and ensure markdown links are preserved
                final_text = ''.join(translated_text).strip()
                final_text = final_text.replace('] (', '](')
                
                return final_text
            
        except anthropic.APIConnectionError as e:
            logger.error(f"Connection error during translation: {e}")
            return text
        except anthropic.RateLimitError as e:
            logger.error(f"Rate limit exceeded during translation: {e}")
            return text
        except anthropic.APIStatusError as e:
            logger.error(f"API error during translation: {e}")
            return text
        except Exception as e:
            logger.error(f"Unexpected error during translation: {e}")
            return text

    def get_provider(self):
        if self.__client is None:
            self.__client = anthropic.Anthropic(api_key=self.__api_key)
        return self.__client

    @classmethod
    def from_settings(cls, settings):
        engine_settings = getattr(settings, cls.settings_key, {})
        return cls(**engine_settings)
