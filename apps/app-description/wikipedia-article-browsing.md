# Wikipedia — Article Browsing

Wikipedia is a free online encyclopedia. This environment covers the **anonymous reader** surface: searching, reading articles, navigating via table of contents and internal links, and browsing related categories. No account or login is required.

## Components to Implement

### Search
- Top-bar search input with live suggestions (dropdown of matching article titles as the user types)
- Search results page: list of articles with title, short description, snippet (bolded keyword matches), last-modified date
- Sort options: Relevance, Alphabetical, Most viewed, Last modified
- Namespace filter (Article, Talk, Category, Help)
- "Did you mean..." suggestion for typos

### Article Page
- Article title as H1
- Status badges under title: "Featured article", "Good article", "Protected", "Stub" (where applicable)
- Last-modified timestamp, page ID, contributor count
- Collapsible table of contents (TOC) on the left with heading hierarchy
- Article body with section headings, inline links to other articles (blue for existing, red for missing)
- Infobox on the right with key/value facts
- Image thumbnails with caption; click to open lightbox (caption, license, full-size)
- Footnote references (click superscript → scroll to References section and highlight entry)
- "See also", "References", "External links" sections at the bottom
- Categories footer: horizontal chip list of categories the article belongs to (each clickable)

### Page Actions Toolbar
- Read / View source / View history tabs
- "View history" shows revision list: timestamp, editor, byte diff, comment — up to 20 revisions
- Star to watch page (toggle, client-side only)
- Cite this page (opens modal with citation formats: APA, MLA, Chicago, BibTeX)
- Download as PDF / Printable version (no-op buttons with confirmation toast)

### Language Switcher
- Sidebar dropdown listing 15 available languages for the current article
- Click language → switches article content to a seeded translation variant

### Category Pages
- Browse articles in a category: alphabetical list grouped by letter, pagination (50 per page)
- Subcategories section at the top

### Random Article
- "Random article" link in sidebar jumps to a randomly-selected seeded article

## Form Controls Summary

- Dropdowns: search-sort, search-namespace, article-language, cite-format (APA/MLA/Chicago/BibTeX)
- Toggles: watch-page (star), TOC-expanded
- Inputs: top-bar search, search-page query

## Seed Data Summary

- **Articles (~20):** Python (programming language), Albert Einstein, Pacific Ocean, Photosynthesis, World War II, Machine Learning, Golden Gate Bridge, Quantum Mechanics, Shakespeare, Tokyo, plus 10 more across history/science/geography/biography
- **Categories (8):** Programming languages, Physicists, Oceans, Biology, 20th-century wars, Bridges, Capital cities, Playwrights
- **Revisions per article:** 10–20 with varied editors and realistic edit comments
- **Infobox fields:** vary per article type (person: born/died/occupation; place: coordinates/population/area; concept: field/discovered by/related)
