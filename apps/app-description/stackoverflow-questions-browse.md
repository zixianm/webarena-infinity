# Stack Overflow — Questions Browse

Stack Overflow is a Q&A site for programmers. This environment covers the **anonymous visitor** surface: browsing the questions feed, filtering by tag, opening question detail with answers and votes, and browsing tag pages. No login required (voting and posting buttons are disabled/prompt, as on the real site).

## Components to Implement

### Questions Feed (`#/questions`)
- Header: "All Questions", total count ("2,341,892 questions"), "Ask Question" button (disabled popover: "Log in to ask")
- Tabs: Newest, Active, Bountied, Unanswered, More (popover with: Frequent, Votes)
- Filter bar: tag chip multi-select (autocomplete input with tag pills), sort dropdown, "filter by no answers / has bounty / has accepted answer" toggles
- Question row: vote count, answer count (green if has accepted answer), view count — then title (link), snippet, tag pills, author row (avatar, reputation, asked time)
- Pagination (15/30/50 per page dropdown + page numbers)

### Question Detail (`#/q/{id}`)
- Title, "Asked N days/months ago", "Modified N ago", "Viewed N times"
- Body: markdown-rendered content with code blocks (syntax-highlighted per language), lists, links
- Tag pills below body
- Vote column on the left (up/down arrows disabled with tooltip), favorite star
- Author block (bottom-right): avatar, display name, reputation, badges, asked-at timestamp
- Comments under question: list of comments, "Add a comment" disabled link
- **Answers section:** header "N Answers", sort dropdown (Highest score, Trending, Date modified, Date created)
- Each answer: vote count, accepted check if applicable (green), body, comments, author block
- "Your Answer" form at the bottom (textarea disabled, "Sign up or log in" inline notice)

### Tag Pages (`#/tags`, `#/tag/{name}`)
- `#/tags`: grid of tag cards (name, question count, short description)
- `#/tag/{name}`: header with tag name and description, Info/Top Questions/Newest/Unanswered tabs, question feed filtered to that tag

### User Pages (`#/u/{id}`)
- Public profile: display name, location, member-since date, reputation, medal counts
- Tabs: Summary (top questions + top answers, recent badges), Answers, Questions, Tags, Activity
- No private actions — view only

### Search (`#/search?q=...`)
- Advanced search hint box at top (e.g., `[javascript] is:question`)
- Filter sidebar: Tags, Answers (has-accepted, has-bounty, no-answers), Score, Views, Asked, Closed
- Results: same question row format

### Left Sidebar (persistent)
- Home, Questions, Tags, Users, Companies (all navigate locally)
- "Collectives" section (static)
- "Teams" promo card

## Form Controls Summary

- Dropdowns: sort (feed/tag/answers), per-page, advanced-filter (no-answers, accepted, bounty)
- Tag multi-select: autocomplete input + chip pills
- Inputs: top-bar search
- Toggles: answer-comment-expand, question-comment-expand, favorite (star)
- Disabled action buttons with tooltips: vote up/down, Ask question, Post answer, Add comment, Post bounty

## Seed Data Summary

- **Tags (~25):** javascript, python, react, typescript, java, c++, sql, git, node.js, html, css, aws, docker, kubernetes, linux, bash, rust, go, ruby-on-rails, django, flask, postgresql, mongodb, android, ios
- **Questions (~30):** varied: "How do I X in Y?" across tags; with 0–8 answers each; 1–3 have accepted answers; a few "closed as duplicate"; realistic scores (-3 to 250), view counts (80 to 1.2M), asked times (minutes to years ago)
- **Answers:** bodies with code blocks, headings, inline code; score from -5 to 180; one marked accepted on most answered questions
- **Users (10):** varied reputation (120 to 250k), badge counts (gold/silver/bronze)
- **Comments:** 0–6 per question/answer, concise (≤200 chars) with realistic gripes/follow-ups
