---
name: RSS News Feeds
description: >
  Teach API-like data fetching with public RSS/Atom feeds: XML parsing, feed
  entries, titles, links, dates, filtering, summaries, caching, and news-source
  responsibility. TRIGGER: RSS feed, Atom feed, news API, XML API, feed parser,
  headlines.
version: 1.0.0
category: Free API
tags: [api, rss, atom, news, xml, feeds, teaching]
---

# RSS News Feeds

## Overview

Use this skill when you want a news-style API lesson without requiring paid news API keys. RSS and Atom feeds are public structured documents, usually XML, and they teach many of the same ideas as APIs.

---

## Security Check

- Use reputable public feeds.
- Respect copyright; do not republish full articles without permission.
- Display source and link back to the original page.
- Cache feeds and do not poll too often.
- Be careful with user-generated or unmoderated feeds.
- Treat feed text as untrusted input if rendering HTML.
- In PowerShell, use `Invoke-WebRequest -UseBasicParsing` for feeds to avoid active content parsing prompts.

---

## Python Feed Parsing

```bash
pip install feedparser
```

```python
import feedparser

feed = feedparser.parse("https://www.nasa.gov/news-release/feed/")

print(feed.feed.get("title"))
for entry in feed.entries[:5]:
    print(entry.get("title"))
    print(entry.get("link"))
```

---

## Without Extra Packages

```python
import urllib.request
import xml.etree.ElementTree as ET

url = "https://www.nasa.gov/news-release/feed/"
xml_text = urllib.request.urlopen(url, timeout=10).read()
root = ET.fromstring(xml_text)

for item in root.findall("./channel/item")[:5]:
    title = item.findtext("title")
    link = item.findtext("link")
    print(title, link)
```

PowerShell safe fetch:

```powershell
$response = Invoke-WebRequest -Uri "https://www.nasa.gov/news-release/feed/" -UseBasicParsing
$response.Content | Select-String "<rss|<feed"
```

---

## Mini Projects

- Headline dashboard.
- Keyword filter.
- Feed comparison page.
- Daily digest generator.
- Topic alerts for robotics, space, weather, or engineering.

---

## Best Practices

- Prefer feedparser for real projects.
- Cache feed results.
- Escape HTML before rendering.
- Show the source and publication date.
- Link users to original articles.
