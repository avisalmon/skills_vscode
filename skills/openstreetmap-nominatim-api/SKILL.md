---
name: OpenStreetMap Nominatim API
description: >
  Teach geocoding and reverse geocoding with OpenStreetMap Nominatim: address
  search, coordinates, map links, user-agent etiquette, rate limits, caching, and
  classroom location apps. TRIGGER: geocoding API, OpenStreetMap, Nominatim,
  address search, reverse geocode, map API, coordinates.
version: 1.0.0
category: Free API
tags: [api, maps, openstreetmap, geocoding, location, json, teaching]
---

# OpenStreetMap Nominatim API

## Overview

Use this skill to teach geocoding: converting place names or addresses into latitude/longitude, and reverse geocoding coordinates back into an address.

Nominatim docs: `https://nominatim.org/release-docs/latest/api/Overview/`

Best for lessons:

- Query parameters.
- URL encoding.
- JSON arrays.
- Coordinates and map links.
- API etiquette and rate limits.

---

## 1. Search Example

Search for a place:

```text
https://nominatim.openstreetmap.org/search?q=Technion%20Haifa&format=json&limit=5
```

Python:

```python
import requests

response = requests.get(
    "https://nominatim.openstreetmap.org/search",
    params={"q": "Technion Haifa", "format": "json", "limit": 5},
    headers={"User-Agent": "api-lesson-demo/1.0"},
    timeout=10,
)
response.raise_for_status()

for place in response.json():
    print(place["display_name"])
    print(place["lat"], place["lon"])
```

---

## 2. Reverse Geocoding

```python
import requests

response = requests.get(
    "https://nominatim.openstreetmap.org/reverse",
    params={"lat": 32.0853, "lon": 34.7818, "format": "json"},
    headers={"User-Agent": "api-lesson-demo/1.0"},
    timeout=10,
)
response.raise_for_status()

data = response.json()
print(data.get("display_name"))
print(data.get("address", {}))
```

---

## 3. Browser Fetch

```javascript
const params = new URLSearchParams({
  q: 'Jerusalem central station',
  format: 'json',
  limit: '5',
});

const response = await fetch(`https://nominatim.openstreetmap.org/search?${params}`);
const places = await response.json();
console.log(places.map(place => [place.display_name, place.lat, place.lon]));
```

For production browser apps, check the current Nominatim usage policy and consider your own backend/cache.

---

## 4. Mini Projects

- Address-to-map-link converter.
- Search box that drops markers on a map.
- Reverse geocode phone GPS coordinates.
- Compare city names in Hebrew and English.
- Combine with Open-Meteo: city name -> coordinates -> weather.

---

## Best Practices

- Send a meaningful User-Agent in scripts.
- Cache repeated lookups.
- Do not bulk geocode large lists on the public service.
- Respect published usage policy.
- Store latitude/longitude as numbers, not strings, after parsing.
- Always handle zero search results.
