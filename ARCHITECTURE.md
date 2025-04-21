# BlogVi (勝利) - Static Blog Generator

BlogVi is a Python-based static site generator designed to create blogs from data sourced from a CSV file (e.g., a published Google Sheet). It uses Jinja2 for templating and supports features like category pages, RSS feeds, article search weighting, and optional translation capabilities.

## Features

*   Generates static HTML blog pages from a remote CSV source.
*   Uses Jinja2 for flexible templating.
*   Creates a main landing page, individual article pages, and category pages.
*   Generates an RSS feed (`rss.xml`).
*   Supports legacy URL slugs for redirects.
*   Configurable via `settings.yaml`.
*   Optional article translation using DeepL or Google Translate.
*   Optional integrations (Google Tag Manager, CommentBox, Sharect).
*   Provides a simple CLI interface.

## Architecture Overview

1.  **Configuration Loading (`_settings.py`, `settings.yaml`):**
    *   The application loads configuration from `settings.yaml` in the project root.
    *   `_settings.py` defines the `Settings` class to hold and provide access to configuration values.
2.  **Data Fetching & Parsing (`core/utils.py`):**
    *   `get_articles_from_csv` fetches the CSV data from the URL specified in `settings.yaml`.
    *   It uses the `requests` library and decodes the response text.
    *   `make_json` parses the CSV text content (using `io.StringIO` and `csv.DictReader`) into a list of dictionaries, where each dictionary represents an article.
3.  **Core Processing (`core/landing.py`, `core/article.py`):**
    *   The main `Landing` object is initialized with the settings.
    *   It iterates through the fetched article dictionaries.
    *   For each valid article (Status '1'), an `Article` object is created (`Article.from_config`).
    *   The `Article` object processes the article data (title, slug, markdown content, categories, etc.).
    *   Articles are added to the `Landing` index, which also manages category groupings.
    *   Legacy slugs are handled by creating redirecting `Article` objects.
4.  **Rendering (`core/landing.py`, `core/article.py`, `templates/`):**
    *   The `Landing.generate()` method orchestrates the rendering process.
    *   It renders the main `index.html` using `templates/blog.html`.
    *   It renders each category page using `templates/category.html`.
    *   Each `Article` object renders its own HTML file (e.g., `article-slug/index.html`) using `templates/article.html`.
    *   Markdown content within articles is converted to HTML during rendering.
    *   An RSS feed (`rss.xml`) is generated using `templates/rss.xml`.
5.  **Translation (Optional, `core/translations/`):**
    *   If `translate_articles` is enabled in settings, the `TranslateEngine` is used.
    *   It interacts with the configured provider (DeepL or Google) to translate article content.
6.  **CLI (`_cli.py`, `setup.py`):**
    *   `setup.py` defines the `blogvi` console script entry point, mapping it to `blog_vi._cli:_cli`.
    *   `_cli.py` uses `click` to define the command-line interface. Currently, it accepts the working directory as an argument.
    *   The `_cli` function calls `generate_blog` (from `__main__.py`) to start the generation process.

## Configuration (`settings.yaml`)

The primary configuration file is `settings.yaml` located in the project root. Key mandatory settings include:

*   `blog_name`: The name of the blog.
*   `blog_root_url`: The base path for blog URLs (used for internal linking, e.g., `/blog`).
*   `blog_post_location_url`: The public URL to the CSV file containing article data.
*   `domain_url`: The full domain URL of the blog (used for RSS feed and absolute links).

Refer to the `settings.yaml` file itself for numerous optional settings related to search, comments, translations, favicons, etc.

## Installation

1.  **Prerequisites:**
    *   Python 3.5+
    *   `pip`
    *   **Build Dependencies for lxml:** You need `libxml2` and `libxslt` development headers. On macOS with Homebrew, install them:
        ```bash
        brew install libxml2 libxslt
        ```
2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/LikaloLLC/BlogVi.git
    cd BlogVi
    ```
3.  **Set up a Virtual Environment (Recommended):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
4.  **Install in Editable Mode:** Editable mode (`-e`) is recommended for development, as it links the installed package to your source code.
    *   **macOS (with Homebrew deps):** Set environment variables to help pip find the build dependencies:
        ```bash
        LDFLAGS="-L$(brew --prefix libxml2)/lib -L$(brew --prefix libxslt)/lib" \
        CPPFLAGS="-I$(brew --prefix libxml2)/include -I$(brew --prefix libxslt)/include" \
        pip3 install -e .
        ```
    *   **Other Systems:** Ensure `libxml2`/`libxslt` headers are discoverable by pip and run:
        ```bash
        pip3 install -e .
        ```
    *   *Troubleshooting:* If you encounter `AttributeError: cython_sources`, ensure `Cython` is listed in `pyproject.toml`'s `build-system.requires` and try reinstalling. If dependency conflicts arise, adjust versions in `requirements.txt`.

## Usage

1.  **Configure `settings.yaml`:** Ensure the mandatory settings (especially `blog_post_location_url`) are correct.
2.  **Generate the Blog:** Run the `blogvi` command from the project root directory, providing `.` as the argument:
    ```bash
    blogvi .
    ```
3.  **Output:** The generated static files (HTML, RSS) will be placed directly in the project root directory.

## Development

*   **Run Locally:** After generating the site, use Python's built-in web server to preview:
    ```bash
    python3 -m http.server 8000
    ```
    Then open `http://localhost:8000` in your browser.
*   **Code Structure:**
    *   `src/blog_vi/`: Main package source code.
        *   `core/`: Core logic (Article, Landing, Utils, Translations).
        *   `templates/`: Jinja2 templates.
        *   `_cli.py`: Click-based CLI definition.
        *   `__main__.py`: Contains `generate_blog` function (called by CLI).
        *   `_settings.py`: Settings class definition.
        *   `_config.py`: Constants like `SETTINGS_FILENAME`.
    *   `settings.yaml`: Main configuration file.
    *   `requirements.txt`: Runtime dependencies.
    *   `setup.py`: Package setup and build configuration.
    *   `pyproject.toml`: Build system requirements.
