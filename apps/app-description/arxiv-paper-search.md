# arXiv — Paper Search and Browse

arXiv is a preprint server for physics, math, CS, biology, and other sciences. This environment covers the **anonymous researcher** surface: searching for papers, browsing by category, reading abstracts, navigating author pages, and viewing the daily listing. No login required.

## Components to Implement

### Home
- Category tree sidebar: Physics (with 12 subcategories), Mathematics (with 32), Computer Science (with 40), Quantitative Biology, Quantitative Finance, Statistics, Electrical Engineering, Economics
- "New submissions" and "Recent" tabs for each category
- "About arXiv", "Submit", "Help" links in header (open static pages)

### Search (`#/search`)
- Simple search: top-bar keyword input with dropdown for field (All fields, Title, Author, Abstract, Comments, Journal ref, ACM classification, MSC classification, Report number, arXiv ID, DOI)
- Advanced search page: multi-row query builder — each row has AND/OR/NOT + field dropdown + term; add/remove row; date range, subject area checklist, abstract-contains input
- Results list: arXiv ID (monospace), title, authors (each clickable), subject tags, submission date, version, links (Abstract, PDF, HTML, BibTeX)
- Per-result expand: abstract preview (first 3 lines), "Show more"
- Sort dropdown: Relevance, Announcement date (newest first), Announcement date (oldest first), Submission date (newest), Submission date (oldest)
- Results per page dropdown (25/50/100/200)
- Pagination

### Paper Detail (`#/abs/{id}`)
- Header: title, authors list (each a link to author page)
- Subject tags (primary in bold, cross-listed after)
- Abstract block
- Comments (e.g., "12 pages, 5 figures, accepted to ICML 2024")
- Journal reference, DOI, Report number
- Submission history: v1, v2, v3 — each with timestamp, byte count, change summary
- Download panel on the right: PDF, HTML (experimental), Source (arXiv-vanity), Formats
- "Cite as" block: bibtex-formatted citation with Copy button
- "Endorsers" (names list), "Access paper" (PDF button)
- "Browse by" links: current author's other papers, related papers (same category)

### Author Page (`#/a/{name}`)
- Name heading, affiliation line
- Papers list (reverse-chronological): same row format as search results
- Coauthor graph (collapsed by default): chip list of top-10 coauthors with paper counts

### Category Listing (`#/list/{cat}/{year-month}`)
- "Showing new submissions received between DATE and DATE"
- Grouped sections: New submissions (N), Cross-lists (M), Replacements (K)
- Each paper rendered in the standard row

## Form Controls Summary

- Dropdowns: search-field, sort-by, per-page, advanced-boolean (AND/OR/NOT per row), advanced-field
- Checkboxes: subject-area (advanced search)
- Text inputs: keyword, author, title, abstract, arxiv-id, date-from, date-to
- Toggles: abstract-expand, coauthor-graph

## Seed Data Summary

- **Papers (~30):** realistic titles across CS (ML, NLP, Systems), Physics (astro-ph, hep-th), Math (topology, combinatorics), Bio (neurons-and-cognition); each with arXiv IDs like `2403.01234`, 1–5 authors, 2–4 subject tags, realistic abstracts (3–6 sentences), 1–3 versions
- **Authors (15):** name, affiliation, 2–6 papers each, ORCID-style IDs
- **Categories:** seed with realistic arXiv codes (cs.LG, cs.CL, math.AT, astro-ph.HE, q-bio.NC, stat.ML, etc.)
- **Saved searches (client-side, 3 items):** e.g., "author: Hinton", "cat: cs.LG AND ti: transformer"
