# Weather.com — Forecast and Multi-Location

Weather.com provides forecasts, radar, and weather news. This environment covers the **anonymous visitor** surface: searching for a location, viewing hourly/daily forecasts, switching units, comparing multiple saved locations, and reading active alerts. No login required.

## Components to Implement

### Location Bar
- Search input with typeahead for city, ZIP, airport code (IATA), coordinates
- "Use current location" button (simulated — selects seed "Current Location: San Francisco, CA")
- Recent locations dropdown (last 5 viewed)

### Saved Locations Strip
- Horizontal chip row of saved locations: each chip shows city, current temp, weather icon, small high/low
- Active chip highlighted; click to load forecast
- "+" button to add current search result to saved list
- "×" on hover to remove a saved location
- Drag to reorder

### Current Conditions Panel (`#/today`)
- Large temperature, feels-like, condition label (e.g., "Partly Cloudy"), weather icon
- Secondary stats grid: Wind (speed + direction arrow), Humidity, Dew Point, Pressure, UV Index (0–11 with category label), Visibility, Sunrise, Sunset, Moon phase
- "As of HH:MM timezone" line below condition
- Active weather alerts banner (red/yellow) — click opens full alert text (title, severity, issued/expires, affected area, description, instructions)

### Hourly Forecast (`#/hourly`)
- Table: next 48 hours, each row has Time, Icon, Condition, Temp, Feels Like, Precip %, Wind, Humidity
- Expand row for additional details (Dew point, Pressure, UV)
- Date separators between days

### 10-Day Forecast (`#/10day`)
- Vertical list: each day shows weekday, date, icon, high/low, condition short, precip %, wind, sunrise/sunset
- Expand row → hourly breakdown for that day

### Radar (`#/radar`)
- Map placeholder (styled div) with play/pause button, timeline scrubber (-1h to +6h), speed toggle (1×/2×/4×)
- Layer toggles: Radar, Satellite, Clouds, Temperature, Precipitation, Wind

### Monthly Outlook (`#/monthly`)
- Calendar grid for current month, each cell shows high/low + icon; hover shows details

### Settings Drawer
- Units: Temperature (°F / °C), Wind (mph / km/h / m/s), Pressure (inHg / hPa / mmHg), Precipitation (in / mm), Distance (mi / km), Time format (12h / 24h)
- "Default location" dropdown (any saved location)
- "Show alerts banner" toggle

## Form Controls Summary

- Dropdowns: units-temperature, units-wind, units-pressure, units-precip, units-distance, time-format, default-location, radar-speed
- Checkboxes/toggles: radar layers, alerts-banner
- Inputs: location-search

## Seed Data Summary

- **Saved locations (5):** San Francisco CA (active), Seattle WA, New York NY, Austin TX, London UK
- **Current conditions (per location):** realistic values with variety (clear, partly cloudy, rainy, snowing)
- **Hourly (48h):** progression with morning/evening pattern, one front passing through
- **Daily (10):** mix of sun/rain/cloud; one weekend with storm alert
- **Alerts:** 1 active (Winter Storm Watch for Seattle, expires tomorrow evening), 1 advisory (Air Quality for NYC)
- **Units on seed:** °F, mph, inHg, in, mi, 12h
