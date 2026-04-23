# ESPN — Scores, Schedules, Standings

ESPN is a sports news and scores site. This environment covers the **anonymous visitor** surface: viewing live and final scores across leagues, browsing schedules by date, viewing standings, reading team and player pages, and filtering news by league. No login required.

## Components to Implement

### League Navigation
- Top-bar with sport tabs: NFL, NBA, MLB, NHL, Soccer, NCAAF, NCAAM, Golf, Tennis, Formula 1
- Date picker below tabs for scores/schedule (calendar + `<` / `>` arrows, "Today" button)
- Secondary nav: Scores, Schedule, Standings, Teams, Stats, News

### Scoreboard (`#/scores/{sport}`)
- Grouped by date (Today, Yesterday, Tomorrow)
- Game card columns: Status badge (Live / Final / Scheduled / Postponed / Delayed), team 1 (logo color swatch, name, score), team 2, game time, network (ESPN / ABC / TNT), betting line (spread, O/U, moneyline)
- Live card: quarter/inning/period indicator, time remaining, possession arrow (where applicable)
- Click card → Game Detail

### Game Detail (`#/game/{id}`)
- Header: away vs home, scores, status
- Tabs: Recap, Box Score, Play-by-Play, Team Stats, Standings
- Box Score: per-player stats table grouped by team
- Play-by-Play: reverse-chronological log of plays with period/time, description, score-after
- Team Stats: side-by-side bars for key metrics (shots, yards, possession%, turnovers, etc.)

### Schedule (`#/schedule/{sport}`)
- Week-based view for football; month-based grid for baseball/basketball
- Filter dropdown: All teams, Division, Conference, My teams (local favorites)
- Sort toggle: by date, by team

### Standings (`#/standings/{sport}`)
- League tabs with sub-tabs per conference/division
- Table: Rank, Team, W, L, (T / OT), PCT, GB/PTS, Home, Away, Div, Conf, Streak, L10
- Click column header to sort

### Team Page (`#/team/{sport}/{id}`)
- Header: logo swatch, team name, record, standing in division
- Tabs: Home, Schedule, Roster, Stats, Depth Chart (sports that have one), Injuries, News
- Roster: table by position with player name, height, weight, age, experience, college
- Injuries: list of players with status (Out, Questionable, Probable, Doubtful, IR), injury type, return estimate

### News (`#/news/{sport}`)
- Feed of articles: headline, subhead, author, timestamp, thumbnail color, tags
- Filter by team, category (News, Analysis, Injuries, Transactions, Fantasy)
- Click article → reading view with body, related articles row at the bottom

### Favorites (client-side)
- "Favorite" star on any team or player — adds to a local favorites panel
- Favorites panel in header shows selected teams' latest games and headlines

## Form Controls Summary

- Dropdowns: sport-tab, date-picker, schedule-filter, standings-sort, news-category
- Tabs: league selector, game-detail tabs, team-detail tabs
- Toggles: favorite (star), standings-by-conference
- Inputs: top-bar search (teams, players, articles)

## Seed Data Summary

- **Sports leagues (5 active):** NFL, NBA, MLB, NHL, Soccer (English Premier League)
- **Teams:** 10 per league with realistic names, city colors, W-L records mid-season
- **Games (across 3 days — yesterday/today/tomorrow):** ~25 with mixed statuses (Live, Final, Scheduled); scores and play-by-play for live/final ones
- **Players per team:** 6–10 with stats (points, rebounds, passing yards, ERA, goals, etc. per sport)
- **News articles (~15):** spread across sports with realistic bylines and timestamps
- **Favorites:** 2 pre-seeded teams, 1 pre-seeded player
