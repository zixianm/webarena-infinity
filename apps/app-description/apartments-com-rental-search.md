# Apartments.com — Rental Search

Apartments.com is a rental listings marketplace. This environment covers the **anonymous renter** surface: searching listings by location, filtering by price and amenities, viewing detail with photos/floorplans/map, saving favorites (client-side), and contacting the listing (form-only). No login required.

## Components to Implement

### Search Header
- Location input: city, neighborhood, ZIP, address, or school district — with typeahead suggestions grouped by type
- Property type dropdown: Apartments, Houses, Townhomes, Condos, Student Housing, Senior Housing, Corporate Housing, Short-Term
- Price-range quick picker (min–max dropdowns with $250 steps)
- Beds quick picker (Studio, 1, 2, 3, 4, 5+)
- "More filters" button opens advanced panel
- Save search chip (client-side saved searches list)

### Results Page (`#/search`)
- Split view: results list (left) + map (right, styled div with pin cluster placeholders)
- Map shows price pins (green/gray depending on hover); hovering a listing highlights its pin
- Sort dropdown: Best match, Price (low→high), Price (high→low), Beds (most→least), Sq ft (largest), Newest, Featured
- View mode toggle: List only / Split / Map only
- Listing card: hero color swatch, "3D tour" / "Video" / "Virtual tour" badges, price range, beds/baths/sqft line, title + address, community amenities chip row, favorite heart toggle, "Request tour" button

### Filters Panel
- Price (min/max slider + inputs)
- Beds (multi-select: Studio, 1, 2, 3, 4, 5+)
- Baths (multi-select: 1+, 1.5+, 2+, 3+, 4+)
- Home type (checkbox: Apartment, House, Townhome, Condo)
- Sqft range slider
- Year built / Year renovated min
- Move-in date picker
- Pet policy (Cats allowed, Small dogs, Large dogs, No pets)
- Laundry (In unit, Shared, None)
- Parking (Garage, Covered, Assigned, Street)
- A/C, Heat, Dishwasher, Hardwood, Fireplace, Balcony, Patio, Pool, Gym, Roof deck, Elevator, Doorman, Concierge, Bike storage, Package receiving (each a checkbox)
- Accessibility (Wheelchair access, Elevator, Roll-in shower)
- Utilities included (Water, Gas, Electricity, Internet, Trash)
- Lease term (Short-term, 3–6 months, 6–12 months, 12+ months, Month-to-month)
- Income restrictions toggle
- Section 8 accepted toggle
- "Clear all" + active-filter chip row above results

### Listing Detail (`#/listing/{id}`)
- Hero: image carousel (5 swatches) with thumbnails, "3D tour" and "Video" tabs, "View all N photos" button
- Title, address, "Available from DATE"
- Price badge + beds/baths/sqft summary
- **Floorplans section:** cards per floorplan — name, beds/baths, sqft, price range, availability count, "View" opens modal with floorplan diagram
- Property overview tabs: Description, Amenities, Fees & Policies, Neighborhood, Schools, Transit, Reviews, Similar rentals
- **Amenities:** two-column grouped list (Unit features, Community features, Accessibility)
- **Fees & Policies:** application fee, security deposit, pet fee, pet rent, parking fee, utilities included, lease terms, smoking policy
- **Neighborhood:** walk score, transit score, bike score cards + nearby locations (groceries, restaurants, parks, transit stops)
- **Schools:** elementary/middle/high with GreatSchools 1–10 rating and distance
- **Reviews:** star summary (with histogram), filter by category (Location, Value, Noise, Office Staff, Maintenance, Grounds), list with date + author + rating + text
- Contact form: Full name, Email, Phone, Move-in date, Message (prefilled template), "Send email" button
- "Schedule tour" button opens time-picker modal (date + time slots)
- Similar rentals row

### Saved Listings (`#/saved`)
- Grid/list toggle, sort options
- "Contacted" badge on any listing where the user submitted the contact form
- Remove button per row

### Saved Searches (`#/searches`)
- Named searches with criteria summary
- Email frequency dropdown (Daily, Weekly, Never — visual only)
- Delete per row

## Form Controls Summary

- Dropdowns: property-type, sort, lease-term, email-frequency, min-price, max-price
- Multi-selects: beds, baths, home-type, pet-policy, parking, laundry, utilities-included
- Sliders: price, sqft, year-built
- Date picker: move-in
- Checkboxes: ~30 amenities + accessibility
- Toggles: favorite (heart), section-8, income-restrictions, view-mode (List/Split/Map)
- Inputs: location, contact form fields

## Seed Data Summary

- **Listings (~20):** spread across Seattle, San Francisco, Austin, NYC, and Chicago; mix of single-family, mid-rise apartment, high-rise condo, student housing; price ranges $800–$8500; beds 0–4
- **Floorplans:** 2–4 per multi-unit listing with varied beds/baths/sqft and availability
- **Reviews:** 3–12 per listing with category ratings and realistic text
- **Saved listings:** 3 pre-saved
- **Saved searches:** 2 (e.g., "SF 2bd under $4000", "Austin pet-friendly house")
- **Neighborhoods data:** realistic walk/transit/bike scores (0–100)
