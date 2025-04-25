# SEO Improvements for article.html

This file tracks planned SEO enhancements for the `templates/article.html` template and related components.

## Meta Tags

- [x] Add `<link rel="canonical" href="{{ settings.domain_url }}{{ article.url }}">`
- [x] Add `<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />`
- [x] Add `<meta property="article:published_time" content="{{ article.timestamp.isoformat() }}">`
- [x] Add `<meta property="article:modified_time" content="{{ article.modified_timestamp.isoformat() }}">` 

## Structured Data (JSON-LD)

- [x] Update `BlogPosting` schema's `dateModified` to use `article.modified_timestamp` 
- [x] Add `BreadcrumbList` schema (Requires visible breadcrumbs on page)
- [x] Add `WebSite` schema (Optional: include `SearchAction`)
- [x] Enhance `Article` schema with `wordCount` and `articleSection` (Requires backend update)
- [x] Review and implement schema interlinking using `@id` where appropriate.

## On-Page Content & Structure

- [x] Implement visible breadcrumb navigation.
- [x] Add an automated Table of Contents (TOC) for longer articles based on headings.
    - [x] Ensure a distinct Author Box with image, name, and bio is present.
- [ ] Verify semantic HTML usage (`<article>`, `<main>`, logical heading structure `<h1>`, `<h2>`, etc.).

## Performance

- [ ] Add `<link rel="preconnect">` for critical external domains (e.g., fonts).
- [ ] Ensure images below the fold use `loading="lazy"`.

## Backend Updates (`src/blog_vi/core/article.py`)

- [x] Modify `Article` class to determine and store `modified_timestamp`.
- [x] Modify `Article` class to calculate and store `wordCount`.
- [ ] (Optional) Modify `Article` class to calculate and store estimated `readingTime`.

## UI/UX Enhancements

- [ ] Enhance Breadcrumbs Styling: Make them more visually distinct and less blended into the background.
- [x] Make CTA Configurable: Allow title, text, button text, and URL to be set via `settings.yaml`. (Done in Step 604)
- [ ] Improve CTA Design: Refine visual presentation, spacing, and integration into the sidebar.
- [ ] Refine Visual Hierarchy: Adjust styling of meta info (author, date, tags), social icons, and TOC to guide the eye better.
- [ ] Improve TOC Visual Appeal: Make the Table of Contents more engaging visually.
- [ ] Adjust Spacing and Alignment: Improve spacing between elements (title, meta, CTA, body) to reduce crowding. Balance sidebar/content width.
- [ ] Enhance Color and Contrast: Introduce subtle color variations or accents to make the design less flat. Use contrast to create visual breaks.
- [ ] Refine Typography: Use font sizes/weights more effectively to create contrast between sections.
- [ ] Add Interactivity: Consider adding subtle hover effects or transitions to elements like links, buttons, or the TOC.
