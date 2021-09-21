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
    'deepl_translator': {},
    'translation_list': [],
    'translate_articles': None,
    'source_abbreviation': None,
}
