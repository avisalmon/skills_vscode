---
name: Public Holidays API
description: >
  Use free public holiday APIs to build calendars, school planners, country
  comparisons, countdowns, and date-based apps. Covers country codes, years,
  local names, global vs regional holidays, and date parsing. TRIGGER: holidays
  API, public holidays, calendar API, Nager.Date, school calendar.
version: 1.0.0
category: Free API
tags: [api, holidays, calendar, dates, countries, json, teaching]
---

# Public Holidays API

## Overview

Use this skill to teach simple date-based APIs. Nager.Date provides public holiday data for many countries without requiring an API key.

Docs: `https://date.nager.at/Api`

---

## Security Check

- No key needed.
- No personal data involved.
- Holiday definitions can vary by region and source.
- Do not assume it covers school vacation days.
- Cache repeated class calls.

---

## Get Holidays for a Country

```python
import requests

year = 2026
country = "IL"
response = requests.get(
    f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country}",
    timeout=10,
)
response.raise_for_status()

for holiday in response.json():
    print(holiday["date"], holiday["localName"], holiday["name"])
```

---

## Check If Today Is a Holiday

```python
import datetime as dt

today = dt.date.today().isoformat()
holidays = response.json()
match = [h for h in holidays if h["date"] == today]

if match:
    print("Holiday today:", match[0]["localName"])
else:
    print("No public holiday today in this dataset")
```

---

## Mini Projects

- Holiday calendar.
- Country comparison.
- Countdown to next holiday.
- Workday calculator.
- School event planner.

---

## Best Practices

- Use ISO country codes.
- Parse dates as dates, not strings, when comparing.
- Show source and year.
- Verify local/regional holidays before relying on the data.
