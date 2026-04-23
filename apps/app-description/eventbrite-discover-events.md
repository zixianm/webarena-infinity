# Eventbrite — Discover Events

Eventbrite is an event discovery and ticketing platform. This environment covers the **anonymous attendee** surface: discovering events by location/date/category, viewing event detail with ticket tiers, saving to a local "Liked events" list, and starting checkout (form only, no payment). No login required.

## Components to Implement

### Discover (`#/discover`)
- Top hero strip: location picker (city, ZIP, "Use current location", or "Online") and date picker (Today, Tomorrow, This weekend, This week, Next week, This month, Pick a date / range)
- Category chip row: Music, Nightlife, Performing Arts, Holidays, Health, Hobbies, Business, Food & Drink, Sports & Fitness, Travel & Outdoor, Charity & Causes, Family & Education, Seasonal, School Activities
- Format chip row: Class, Conference, Festival, Party, Concert, Networking, Meetup, Workshop, Expo, Screening
- Price chip row: Free, Paid
- Curated collections: "Trending near you", "This weekend", "Online events", "Free events", "Black-owned businesses", "Just announced"
- Featured events carousel

### Search Results (`#/search?q=...`)
- Left: filter sidebar (category, format, price, date, language, currency)
- Right: event card grid — each card has hero color swatch, date badge (top-left), title, venue + city, price range (Free / "From $X"), organizer name, "Like" heart toggle, attendee-count snippet
- Sort: Relevance, Date, Distance, Price, Popularity
- Map toggle (map view with price pins)
- "Events you might like" row at the bottom

### Event Detail (`#/event/{id}`)
- Hero image (color swatch), title, date/time (with timezone), venue (address, map preview), organizer name (with follower count + Follow button)
- "Get tickets" CTA scrolls to ticket section (sticky on mobile)
- About the event (rich text), Agenda (timeline of sessions), Speakers (avatar + name + role grid)
- Location panel: embedded map (styled), transit/parking notes, directions link
- **Tickets section:** list of tiers — General Admission, VIP, Early Bird, Group (4+), Student. Each shows name, description, price (or "Free"), availability count / status (Available / Selling fast / Sold out / Ended), stepper for quantity (min/max per order)
- Promo code input with "Apply" button (accepts seed codes: WELCOME10, EARLY50, STUDENT)
- Refund policy block
- Tags row, Share modal (copy link, social icons)
- Reviews / ratings summary (if event has past instances)
- "More events by this organizer" section
- "Similar events" section

### Checkout (`#/checkout/{id}`)
- Order summary panel (sticky): event name, date, selected tickets, subtotal, fees, promo discount, total
- Attendee info form: for each ticket, collect First name, Last name, Email, Phone (optional), Dietary restrictions (optional textarea), T-shirt size (dropdown when applicable)
- Contact info section (primary buyer): name, email, billing country dropdown
- Payment section (form fields only; no real payment): card number, expiry, CVC, ZIP — or "Apple Pay" / "Google Pay" buttons (no-op)
- "Register" / "Place order" button opens confirmation modal with order number and "Add to calendar" button
- Countdown timer (e.g., 10:00) for holding tickets; resets on reset

### Liked Events (`#/liked`)
- Grid of hearted events with unheart button, "Remove all" action
- Sort: recently liked, event date

### Following (`#/following`)
- List of followed organizers with unfollow button and latest events

### Organizer Page (`#/org/{id}`)
- Header: logo swatch, name, follower count, Follow toggle, description
- Upcoming events grid, Past events grid, Reviews

## Form Controls Summary

- Dropdowns: location, date-preset, sort, billing-country, tshirt-size, currency, language
- Multi-selects: category, format, price-type, sub-category
- Chip rows: category, format, price
- Steppers: ticket quantity (per tier)
- Inputs: search, promo code, attendee info, contact info, card form
- Toggles: like (heart), follow (organizer), map-view, online-only

## Seed Data Summary

- **Events (~20):** mix across SF, NYC, Austin, Seattle, and "Online"; categories: tech conference, live concert, cooking class, 5K run, art workshop, networking mixer, film festival, book signing, yoga retreat, trivia night; dates spanning next 60 days
- **Organizers (8):** varying follower counts (340 – 52k), 1–4 upcoming events each
- **Ticket tiers per event:** 2–5 tiers with realistic pricing ($0 free → $450 VIP)
- **Promo codes:** WELCOME10 (10% off), EARLY50 ($50 off), STUDENT (25% off, single-use per email)
- **Liked events:** 2 pre-liked
- **Following:** 1 pre-followed organizer
