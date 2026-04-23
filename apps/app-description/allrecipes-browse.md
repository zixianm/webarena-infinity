# AllRecipes — Browse and Filter

AllRecipes is a recipe discovery site. This environment covers the **anonymous visitor** surface: browsing recipes by category, filtering by diet and ingredients, viewing recipe detail with steps and ratings, and saving items to a local (client-side) "cookbook". No login required.

## Components to Implement

### Home / Category Browse
- Hero carousel of 5 featured recipes (title, image color, rating stars, reviewer count)
- Category chip row: Breakfast, Lunch, Dinner, Dessert, Appetizers, Drinks, Vegan, Gluten-Free, Quick (≤30 min), Kid-Friendly
- Grid of recipe cards per category: title, hero color, star rating (1 decimal), review count, cook time, difficulty badge
- "Load more" pagination

### Recipe Detail (`#/recipe/{id}`)
- Header: title, author, rating summary (stars + review count), published date, update date
- Key facts strip: Prep time, Cook time, Total time, Servings (with +/- stepper that scales ingredient amounts), Yield
- "Jump to recipe" button scrolls past the narrative intro to the ingredients section
- Ingredients list (with checkboxes that strike through when checked; client-side)
- Directions list (numbered, with "Mark as done" per step)
- Nutrition panel (calories, fat, carbs, protein, sodium, fiber — per serving; collapsible)
- Tags row: dietary tags, cuisine, meal type
- Photos gallery (4 preset color swatches simulating reviewer photos) with lightbox
- Reviews section: star breakdown histogram, list of reviews (user name, stars, date, text, helpful-count, reply button)
- "Write a review" inline form (star picker + textarea + submit; posts to state)
- "Save to cookbook" button (toggle, client-side)
- "Print", "Share" buttons (open respective modals)

### Filter Panel (on search / category page)
- Diet (multi-select): Vegetarian, Vegan, Gluten-Free, Dairy-Free, Keto, Paleo, Low-Carb
- Cuisine (multi-select): Italian, Mexican, Asian, American, Mediterranean, French, Indian
- Time (radio): Any, Under 15 min, Under 30 min, Under 1 hr, 1 hr+
- Difficulty (radio): Any, Easy, Medium, Hard
- Rating (radio): Any, 3★+, 4★+, 4.5★+
- Ingredients to include (chip input), Ingredients to exclude (chip input)
- Sort (dropdown): Most popular, Highest rated, Newest, Quickest

### Search (`#/search?q=...`)
- Input in top nav with typeahead (8 suggestions + "Searches" heading)
- Results page: same card grid + filter panel; active-filter chips shown above grid with "Clear all"

### Cookbook (`#/cookbook`)
- List of saved recipes (thumbnail + title + rating)
- "Unsave" per row, "Clear cookbook" button
- Organize into user-created folders (Breakfast, Weeknight, Date Night, etc.) with drag-to-folder

## Form Controls Summary

- Dropdowns: sort-by (results/category), servings-scaler (stepper)
- Checkbox groups: diet, cuisine
- Radio groups: time, difficulty, rating
- Chip inputs: include/exclude ingredients
- Toggles: save-to-cookbook, ingredient checkbox (per-line), step-done (per-line), nutrition-expand

## Seed Data Summary

- **Recipes (~25):** Chocolate Chip Cookies, Classic Lasagna, Chicken Tikka Masala, Vegan Pad Thai, 30-Minute Chili, Sheet-Pan Salmon, Banana Bread, Sourdough Starter, Caesar Salad, Avocado Toast, Beef Bourguignon, Miso Soup, Vegetarian Enchiladas, Overnight Oats, Pho, Tiramisu, Ratatouille, Shrimp Tacos, Apple Pie, Green Smoothie, Homemade Pizza, Mushroom Risotto, Butter Chicken, Chocolate Brownies, Matcha Latte
- **Reviews:** 5–30 per recipe, varied ratings with realistic text (cooking tips, substitutions, complaints)
- **Cookbook:** 3 pre-saved recipes in a "Weeknight Favorites" folder
- **Search history:** 5 recent queries (e.g., "pasta", "30 min dinner", "vegan dessert")
