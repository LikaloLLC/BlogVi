# BlogVi Design Overview

This document provides a high-level overview of the BlogVi project structure, key components, and workflow.

## Project Goal

BlogVi is a static blog generation system designed to create blog posts from structured data (like CSV) and Markdown content, render them using templates, and apply modern styling.

## Core Technologies

*   **Backend:** Python
*   **Templating:** Jinja2
*   **Styling:** Tailwind CSS (including the `@tailwindcss/typography` plugin for `prose` styling)
*   **Data:** CSV for article metadata, Markdown for main content.

## Key Components

1.  **Configuration (`settings.yaml`)**:
    *   Located in the project root.
    *   Defines blog name, URLs, author defaults, features (comments, social sharing, GTM), and other site-wide settings.
    *   Supports environment variables for sensitive keys (e.g., API keys).

2.  **Core Logic (`src/blog_vi/core/`)**:
    *   `article.py`: Contains the `Article` class, likely responsible for processing individual article data (metadata + markdown) and preparing it for rendering.
    *   `landing.py`: Contains `Landing` and `CategoryLanding` classes, managing the generation of the main landing page and category index pages.
    *   `utils.py`: Includes helper functions, notably `get_articles_from_csv` which fetches and cleans article metadata from a CSV source URL using `requests` and `ftfy`.
    *   `translations/`: Contains logic for translation providers (DeepL, Google).

3.  **Templates (`templates/`)**:
    *   Standard Jinja2 templates.
    *   `blog.html`: The base template providing the overall page structure (header, footer, navigation, main content block). It includes CSS links (likely Tailwind output) and JS. Currently has unresolved lint errors around lines 275 & 299.
    *   `article.html`: Template specifically for rendering individual blog posts. It extends `blog.html` and defines blocks for the title, author information, main content (`{% include content %}`), comments, etc. Recent work focused on restructuring the author block (avatar, name, date, read time, categories, bio, social links) below the main title.
    *   Other templates likely exist for the landing page, category pages, RSS feed, etc.

4.  **Styling**:
    *   Primarily uses Tailwind CSS utility classes directly within the HTML templates.
    *   The `prose` class (from `@tailwindcss/typography`) is used to apply default styling to the main article content generated from Markdown. Proper application scope of `prose` is crucial (should typically wrap only the Markdown-generated content).

5.  **Content Source**:
    *   Article metadata (title, author, date, categories, etc.) is sourced from a CSV file fetched via URL (`utils.get_articles_from_csv`).
    *   The main body of each article is likely stored as Markdown files, referenced or included based on the CSV data.

6.  **Generation Process**:
    *   A script (likely `regen_blog.sh`) orchestrates the process:
        *   Fetching data.
        *   Processing articles and landing pages using the core Python classes.
        *   Rendering Jinja2 templates with the processed data.
        *   Outputting static HTML files to a designated output directory (e.g., `dist/` or `public/`).
        *   Potentially running a local development server (`python -m http.server` or similar).

## Recent Focus & Issues

*   **Author Section Layout (`article.html`)**: Efforts were made to restructure the author details section (moving it below the `h1` title, adjusting spacing, separating categories onto a new line, filtering empty categories). However, these changes led to broader layout/styling issues, potentially due to incorrect nesting or interference with the `prose` styling scope. The USER has reverted these changes.
*   **Lint Errors (`blog.html`)**: Persistent lint errors (Property assignment expected, Declaration or statement expected) exist around lines 275 and 299, needing investigation.
*   **Styling**: Ensuring Tailwind CSS classes, especially `prose`, are applied correctly and scoped appropriately is important for maintaining consistent design.