# MDN Web Docs — Reference Browsing

MDN Web Docs is Mozilla's documentation site for web standards (HTML, CSS, JavaScript, Web APIs). This environment covers the **anonymous reader** surface: browsing references, searching, filtering by technology, reading with inline examples and browser-compatibility tables. No login required.

## Components to Implement

### Global Navigation
- Top nav: MDN logo, section links (References, Guides, Plus, Blog), search bar
- "References" dropdown: HTML, CSS, JavaScript, HTTP, Web APIs, Web Extensions, Accessibility, SVG, MathML
- Theme switcher (Light / Dark / OS default)
- Language dropdown (en-US, es, fr, ja, ko, pt-BR, ru, zh-CN, zh-TW)

### Search
- Input with typeahead suggestions (top 8 matches: title + short breadcrumb)
- Full results page: title, breadcrumb (e.g., "JavaScript > Array > Array.prototype.map"), short description, snippet with highlighted terms
- Filter by: Technology (checkbox list), Page type (Reference, Guide, Tutorial, Glossary), Sort by Relevance / Popularity / Recently updated

### Reference Page
- Breadcrumb above title (clickable hierarchy)
- Title with category badge ("Experimental", "Deprecated", "Non-standard" where applicable)
- Left sidebar: in-category navigation tree (current page highlighted)
- "In this article" right-rail TOC (sticky, sections highlighted as scrolled)
- Content: description, syntax block, parameters table, return value, examples (with copy-to-clipboard button), notes
- **Browser compatibility table:** desktop and mobile browsers (Chrome, Edge, Firefox, Safari, Opera, Chrome Android, Firefox Android, Safari iOS, Samsung Internet) with supported version or "No" / "Yes" / version number
- **Specifications table:** spec name + section link
- "See also" list at the bottom

### Interactive Examples
- Embedded code editor area with tabs (HTML / CSS / JS) and a live preview pane
- "Reset" button reverts to seed example
- "Open in Playground" link (no-op)

### Bookmarks (client-side only)
- Star icon toggles a page into a bookmarks list (stored in state, not server)
- `#/bookmarks` page lists bookmarked articles with unbookmark button

## Form Controls Summary

- Dropdowns: References menu, language, sort-by, theme
- Checkboxes: Technology filter, Page-type filter
- Toggles: dark mode, bookmark, "In this article" collapse, browser-compat expand-all
- Inputs: global search, in-example code editor

## Seed Data Summary

- **Reference pages (~30):**
  - JavaScript: `Array.prototype.map`, `Array.prototype.filter`, `Promise`, `async/await`, `fetch`, `addEventListener`
  - CSS: `flexbox`, `grid`, `:hover`, `transform`, `@media`, `var()`
  - HTML: `<input>`, `<form>`, `<button>`, `<dialog>`, `<picture>`
  - Web APIs: `fetch()`, `localStorage`, `IntersectionObserver`, `WebSocket`
  - HTTP: `Cache-Control`, status codes, `CORS`
- **Guides (5):** Using Promises, CSS Grid overview, Introduction to Fetch, Accessible forms, Responsive images
- **Browser compat:** realistic version numbers, at least one feature with "Non-standard" badge and one "Deprecated"
- **Search history:** 10 recent queries (client-side)
- **Bookmarks:** 3 pre-seeded
