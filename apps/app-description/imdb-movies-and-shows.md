# IMDb — Movies and Shows Browsing

IMDb is a movie and TV database. This environment covers the **anonymous visitor** surface: searching titles and people, viewing title detail pages (cast, crew, ratings, trivia), browsing Top 250 and Popular lists, and filtering by genre/year. No login required (no watchlist requiring sign-in; the local "watchlist" is client-side only).

## Components to Implement

### Search
- Top-bar input with category dropdown: All, Titles, TV Episodes, Celebs, Companies, Keywords
- Typeahead with grouped suggestions (Titles ▸ Celebs ▸ Keywords), each with thumbnail + year
- Full search results page: filter sidebar (Title type, Genre, Rating, Year, Runtime, Language, Country), grid/list view toggle, sort (Popularity / IMDb rating / Number of votes / Release date / Alphabetical)

### Title Detail (`#/title/{id}`)
- Hero block: poster swatch, title, year, certificate (PG/PG-13/R/TV-MA), runtime, genre chips
- IMDb rating card: 10-star bar, rating (1 decimal), vote count, "Rate this" (1–10 picker; client-side)
- Metascore badge (0–100), Popularity rank (with up/down arrow)
- Trailer thumbnail (plays inline modal with play/pause/seek/scrubber)
- Top cast horizontal list (10 actors with character name)
- Storyline (synopsis + plot keywords chip row)
- Details section: release date, countries, languages, production companies, budget, box office (opening / gross US / gross worldwide)
- Tech specs: Runtime, Sound mix, Color, Aspect ratio
- Tabs below hero: Cast & crew, Episodes (TV only), User reviews, Trivia, Goofs, Quotes, Connections, Soundtrack, FAQ
- **Cast & crew page:** full list grouped by role (Directed by, Writing credits, Cast, Produced by, Music, Cinematography, Editing, …)
- **User reviews page:** each review has rating stars, title, author, date, spoiler toggle (spoiler hides body until clicked), helpful-count (Up/Down with counter)

### Top 250 (`#/chart/top`)
- Numbered list, each row: rank, poster, title, year, rating, vote count, your-rating cell, add-to-watchlist button
- Sort dropdown, filter panel (Genre, Decade, Your rating)

### Most Popular Movies (`#/chart/moviemeter`)
- Numbered list with popularity rank and movement arrow

### Person Page (`#/name/{id}`)
- Photo, name, known-for, birth date/place, height, bio (collapsible)
- Filmography by role (Actor, Director, Producer, …), each section shows year + title + role
- Awards summary (won/nominated counts with expand to full list)

### Watchlist (`#/watchlist`, client-side)
- List of added titles with bulk actions (Remove, Mark as watched)
- Sort options, filter by genre/type

## Form Controls Summary

- Dropdowns: search-category, results-sort, chart-sort, person-filmography-role, title-reviews-sort, title-type
- Multi-select (filter sidebar): Genre, Country, Language, Certificate
- Range sliders: Rating (0–10), Year (1920–current), Runtime (0–300 min)
- Inputs: keyword search
- Toggles: watchlist (per title), spoiler reveal, helpful up/down per review, grid/list view

## Seed Data Summary

- **Titles (~30):** mix of all-time classics (The Godfather, Casablanca, 12 Angry Men), modern blockbusters (Inception, The Dark Knight, Interstellar), award winners (Parasite, Everything Everywhere All at Once, Oppenheimer), and TV series (Breaking Bad, The Wire, Succession, The Bear); realistic ratings (7.2–9.3), vote counts (50k–2M)
- **People (15):** directors (Nolan, Scorsese, Bong Joon-ho), actors (Meryl Streep, Denzel Washington, Tilda Swinton); each with 3–6 credits
- **Top 250:** subset of seed titles in ordered positions
- **Reviews per title:** 3–15 with varied sentiment (some with spoiler flag)
- **Watchlist:** 2 pre-seeded titles
