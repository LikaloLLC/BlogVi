SETTINGS_FILENAME = 'settings.yaml'
AUTHORS_FILENAME = 'authors.yaml'
DEEPL_API_KEY = ''

SETTINGS_DEFAULTS = {
    'link_menu': [],
    'search_config': {
        'title': {
            'weight': 8
        },
        'summary': {
            'weight': 6
        },
        'author_name': {
            'weight': 5
        },
        'categories': {
            'weight': 3
        }
    },
    'comments': {
        'enabled': False,
    },
    'google_tag_manager': {
        'enabled': False
    },
    'subscribe': {
        'enabled': False
    },
    'sharect': {
        'enabled': False
    },
    'landing_meta': {
        'title': '',
        'description': '',
        'image': '',
        'keywords': '',
        'url': '',
        'author': ''
    },
    'translator': None,
    'google_translator': {},
    'deepl_translator': {},
    'claude_translator': {},
    'translation_list': [],
    'translate_articles': None,
    'show_language_picker': False,
    'source_language': {},
    'source_abbreviation': None,
    'favicons': [],
    # Default Call to Action settings
    'call_to_action': {
        'enabled': False, # Disabled by default
        'title': 'Default CTA Title',
        'text': 'Default CTA description text.',
        'button_text': 'Learn More',
        'button_url': '#'
    }
}
