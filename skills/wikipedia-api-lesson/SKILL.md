---
name: Wikipedia API
description: >
  Teach API usage with Wikimedia/MediaWiki: search articles, fetch summaries,
  parse page data, use query parameters, handle CORS, respect API etiquette, and
  build knowledge apps. TRIGGER: Wikipedia API, Wikimedia API, MediaWiki API,
  article search, wiki data.
version: 1.0.0
category: Free API
tags: [api, wikipedia, wikimedia, mediawiki, search, json, teaching]
---

# Wikipedia API

## Overview

Use this skill to teach API fundamentals with Wikipedia and Wikimedia data. Students already understand the domain, so they can focus on URLs, query parameters, JSON, and respectful API use.

MediaWiki API docs: `https://www.mediawiki.org/wiki/API:Main_page`

---

## 1. Simple Article Summary

Wikipedia REST summary endpoint:

```text
https://en.wikipedia.org/api/rest_v1/page/summary/Computer_programming
```

Python:

```python
import requests

url = "https://en.wikipedia.org/api/rest_v1/page/summary/Computer_programming"
headers = {"User-Agent": "api-lesson-demo/1.0"}

response = requests.get(url, headers=headers, timeout=10)
response.raise_for_status()
data = response.json()

print(data["title"])
print(data.get("extract"))
print(data.get("content_urls", {}).get("desktop", {}).get("page"))
```

---

## 2. Search Articles

MediaWiki Action API search:

```python
import requests

response = requests.get(
    "https://en.wikipedia.org/w/api.php",
    params={
        "action": "query",
        "list": "search",
        "srsearch": "robotics",
        "format": "json",
    },
    headers={"User-Agent": "api-lesson-demo/1.0"},
    timeout=10,
)
response.raise_for_status()

data = response.json()
for result in data["query"]["search"][:5]:
    print(result["title"], result["pageid"])
```

---

## 3. Browser Fetch with CORS

For browser demos, add `origin=*` to unauthenticated Action API calls:

```javascript
const params = new URLSearchParams({
  action: 'query',
  list: 'search',
  srsearch: 'robotics',
  format: 'json',
  origin: '*',
});

const response = await fetch(`https://en.wikipedia.org/w/api.php?${params}`);
const data = await response.json();
console.log(data.query.search.map(item => item.title));
```

---

## 4. Good Mini Projects

- Article search box.
- Random article viewer.
- Summary card for a topic.
- Compare search results in English and Hebrew Wikipedia.
- Link preview generator.
- Classroom glossary builder.

---

## 5. API Etiquette

Teach students to:

- Send a meaningful User-Agent in server-side scripts.
- Avoid aggressive loops.
- Cache repeated results.
- Handle missing pages.
- Respect terms of use.
- Prefer read-only demos unless teaching authenticated editing intentionally.

---

## Best Practices

- Start with summary endpoint for quick success.
- Use Action API for search and advanced queries.
- Add `origin=*` for unauthenticated browser calls.
- Treat snippets as HTML unless documentation says plain text.
- Show students how to inspect the full JSON before coding assumptions.
