---
name: NASA Open APIs
description: >
  Teach REST API fundamentals with NASA public data: APOD, asteroid data, Earth
  events, image search, API keys, DEMO_KEY limits, response headers, JSON parsing,
  and classroom space-data projects. TRIGGER: NASA API, APOD, asteroid API,
  space API, image API, DEMO_KEY, API lesson.
version: 1.0.0
category: Free API
tags: [api, nasa, space, apod, json, python, teaching]
---

# NASA Open APIs

## Overview

Use this skill to teach API calls with exciting public space data. NASA APIs are great for demos because many endpoints are visual, surprising, and easy to explain.

For the most reliable first classroom demo, start with NASA Image and Video Library search because it does not require an API key. Use APOD afterward to teach API keys, `DEMO_KEY`, and rate limits.

NASA API portal: `https://api.nasa.gov/`

Good lesson outcomes:

- Understand API keys.
- Read JSON and image URLs.
- Inspect response headers for rate limits.
- Build small apps with real public data.

---

## 1. API Key Basics

NASA examples often use `DEMO_KEY`, which is convenient for first exploration but has low rate limits. For a real class project, students can register for their own key on the NASA API portal.

Never commit a personal API key. Put it in `.env`:

```text
NASA_API_KEY=replace_with_your_key
```

Install helper package:

```bash
pip install requests python-dotenv
```

```python
import os
from dotenv import load_dotenv

load_dotenv()
NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
```

---

## 2. NASA Image Search

NASA Image and Video Library API is useful for no-key search demos.

```python
import requests

response = requests.get(
    "https://images-api.nasa.gov/search",
    params={"q": "moon", "media_type": "image"},
    timeout=10,
)
response.raise_for_status()
data = response.json()

for item in data["collection"]["items"][:5]:
    title = item["data"][0].get("title")
    link = item["links"][0].get("href") if item.get("links") else None
    print(title, link)
```

---

## 3. Astronomy Picture of the Day

```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("NASA_API_KEY", "DEMO_KEY")

response = requests.get(
    "https://api.nasa.gov/planetary/apod",
    params={"api_key": api_key},
    timeout=10,
)
response.raise_for_status()
data = response.json()

print(data["title"])
print(data.get("date"))
print(data.get("url"))
print(data.get("explanation", "")[:300])
```

---

If APOD times out or hits a `DEMO_KEY` limit during class, switch back to image search and explain that real APIs have operational limits.

---

## 4. Check Rate Limit Headers

```python
print("Limit:", response.headers.get("X-RateLimit-Limit"))
print("Remaining:", response.headers.get("X-RateLimit-Remaining"))
```

Teaching point: APIs often communicate operational information through headers, not only JSON bodies.

---

## 5. Mini Projects

- Astronomy picture page.
- Random date APOD explorer.
- Space image search app.
- Asteroid close-approach dashboard.
- Compare JSON body vs response headers.
- Build a cache so repeated classroom demos do not waste quota.

---

## Best Practices

- Use `DEMO_KEY` only for quick demos.
- Put real keys in `.env` and keep `.env` ignored by git.
- Handle rate-limit errors politely.
- Cache responses during lessons.
- Credit NASA data sources when displaying images or text.
