# CarGurus — Used Car Search

CarGurus is an auto marketplace for used and new cars. This environment covers the **anonymous shopper** surface: searching and filtering listings, viewing listing detail with price analysis, saving listings to a local wishlist, and comparing side-by-side. No login required.

## Components to Implement

### Search Header
- Quick filter bar: Make dropdown → Model dropdown → ZIP input → Distance dropdown (10/25/50/75/100/200/500 mi/Nationwide) → Max price input → "Search" button
- Toggle: New / Used / Certified Pre-Owned
- Link: Advanced Search (expands the full filter panel)

### Results Page (`#/search`)
- Two-column layout: filter sidebar (left) + results list (right)
- Results sort: Best Deals, Price (low→high), Price (high→low), Mileage, Distance, Year (newest), Year (oldest), Just listed
- Each listing card: hero color swatch, Year Make Model Trim, price (with "Great Deal / Good Deal / Fair Deal / Overpriced" badge — color-coded), mileage, location/distance, dealer name & rating, features chip row (AWD, Leather, Sunroof, Nav, Backup Camera), "Save" star toggle, "Compare" checkbox
- Pagination / infinite-scroll toggle (user-facing preference)
- Results count and "showing N of M" label

### Filter Sidebar
- Make (multi-select accordion with counts)
- Model (multi-select, filtered by selected makes)
- Price range (dual-handle slider + min/max input)
- Year range (dual-handle slider + min/max input)
- Mileage max (slider)
- Body type (checkbox: Sedan, SUV, Truck, Coupe, Convertible, Hatchback, Van, Wagon)
- Trim (multi-select)
- Exterior color (color swatch multi-select)
- Interior color (swatch multi-select)
- Drivetrain (FWD, RWD, AWD, 4WD)
- Transmission (Automatic, Manual, CVT, DCT)
- Fuel type (Gasoline, Hybrid, Electric, Diesel, Plug-in Hybrid)
- MPG (slider)
- Features (checkbox: Apple CarPlay, Android Auto, Heated seats, Sunroof, Navigation, Backup camera, Leather, Blind-spot monitor, Adaptive cruise)
- Deal rating (Great/Good/Fair only toggle)
- Seller type (Dealer, Private Seller)
- Has photos / Has price / Has financing offer (toggles)
- "Clear all" + active-filter chips row above results

### Listing Detail (`#/listing/{id}`)
- Photo gallery (5 swatches, click to enlarge; prev/next buttons)
- Price block: asking price, CarGurus price analysis bar (Great Deal → Overpriced with marker), "$X below/above market", IMV (Instant Market Value) tooltip
- Financing calculator: price, down payment, term (dropdown 24/36/48/60/72/84), APR (input), trade-in (input) → monthly payment
- Vehicle highlights: Year, Make, Model, Trim, Body, Engine, Transmission, Drivetrain, Fuel, MPG, Exterior/Interior color, VIN (masked last 6), Stock #, Mileage
- Features grid (grouped: Convenience, Entertainment, Safety, Packages)
- Vehicle history summary (accidents reported, owners, service records, rental history — each with badge ✓ or ⚠)
- Dealer info: name, rating (stars + review count), address, phone, distance, hours, inventory count, "View all inventory" link
- Actions: Save, Compare, Check availability (modal — name/email/phone form, stays local), Get dealer's price, Share, Report listing

### Compare (`#/compare`)
- Up to 4 listings side-by-side in a table: row groups for Pricing, Specs, Features, Dealer
- Remove listing button per column, "Add another" selector

### Saved (`#/saved`)
- Grid/list toggle, sort by recently added
- "Remove all saved", per-row remove

## Form Controls Summary

- Dropdowns: make, model, distance, sort-by, financing-term
- Multi-selects: make, model, trim, body-type, colors, features, fuel, drivetrain, transmission, seller-type
- Sliders: price range, year range, mileage, MPG
- Inputs: ZIP, max price, down payment, APR, trade-in value
- Toggles: save (star per listing), compare (checkbox), new/used/CPO, pagination preference, deal-rating-filter, filter toggles (has-photos etc.)

## Seed Data Summary

- **Listings (~25):** mixed Makes (Toyota, Honda, Ford, Chevy, BMW, Tesla, Subaru, Mazda, Hyundai, Audi, Jeep, Ram); years 2015–2024; mileage 1k–120k; price $12k–$85k; varied body types and features; mix of Great/Good/Fair/Overpriced badges
- **Dealers (8):** name, rating 3.6–4.9, review count 45–1200, inventory count 20–350, location within realistic metro areas
- **Saved listings:** 2 pre-saved
- **Compare list:** 0 pre-seeded (user adds)
- **Default search state:** Used, ZIP 94103, 50-mile radius, no filters, sort Best Deals
