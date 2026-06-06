---
name: REST Countries API
description: >
  Teach REST API basics with country data: search by name or code, filter fields,
  currencies, capitals, flags, languages, regions, JSON arrays, and simple data
  dashboards. TRIGGER: REST Countries, country API, flags API, currency API,
  capital city, API lesson.
version: 1.0.0
category: Free API
tags: [api, countries, geography, json, flags, teaching]
---

# REST Countries API

## Overview

Use this skill for a simple and fun first API lesson. REST Countries returns country metadata such as names, capitals, flags, currencies, languages, region, and population.

Docs: `https://restcountries.com/`

Good lesson outcomes:

- Call an endpoint with path parameters.
- Work with JSON arrays.
- Select only fields you need.
- Render images from URLs.
- Build small dashboards.

---

## 1. First Calls

Search by country name:

```text
https://restcountries.com/v3.1/name/israel
```

Filter fields:

```text
https://restcountries.com/v3.1/name/israel?fields=name,capital,flags,currencies,languages,population
```

All countries requires fields:

```text
https://restcountries.com/v3.1/all?fields=name,capital,region,population,flags
```

---

## 2. Python Example

```python
import requests

response = requests.get(
    "https://restcountries.com/v3.1/name/israel",
    params={"fields": "name,capital,flags,currencies,languages,population"},
    timeout=10,
)
response.raise_for_status()

country = response.json()[0]
print(country["name"]["common"])
print("Capital:", country.get("capital", ["Unknown"])[0])
print("Population:", country.get("population"))
print("Flag:", country["flags"].get("png"))
```

---

## 3. JavaScript Example

```javascript
const response = await fetch('https://restcountries.com/v3.1/name/japan?fields=name,capital,flags,population');
if (!response.ok) throw new Error(`HTTP ${response.status}`);

const [country] = await response.json();
console.log(country.name.common, country.capital?.[0], country.flags.png);
```

---

## 4. Mini Projects

- Country search card.
- Flag quiz.
- Sort countries by population.
- Filter countries by region.
- Currency lookup.
- Compare capitals and languages.

---

## Teaching Notes

- Explain why some endpoints return arrays even when there is one result.
- Use optional chaining or defensive checks for missing fields.
- Teach URL encoding with country names that contain spaces.
- Discuss why filtering fields reduces bandwidth.

---

## Best Practices

- Request only the fields needed.
- Handle empty result arrays.
- Do not assume every country has one capital or one language.
- Credit flag/image sources according to the API terms.
