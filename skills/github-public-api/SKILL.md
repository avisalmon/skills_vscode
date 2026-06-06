---
name: GitHub Public API
description: >
  Use GitHub's public REST API for classroom projects: search repositories, read
  issues, inspect commits, list contributors, understand pagination, rate limits,
  User-Agent headers, and optional token authentication. TRIGGER: GitHub API,
  repositories API, issues API, commits API, GitHub REST, public API.
version: 1.0.0
category: Free API
tags: [api, github, repositories, issues, commits, json, teaching]
---

# GitHub Public API

## Overview

Use this skill to teach APIs with real software-engineering data. Students can search repositories, inspect issues, read commit metadata, and learn pagination/rate limits.

Docs: `https://docs.github.com/rest`

Many read-only calls work without a token, but rate limits are lower. Tokens are optional and must be stored in `.env`, never in code.

---

## Security Check

- Use only public repository data in class.
- Do not ask students for personal access tokens unless needed.
- Never commit `GITHUB_TOKEN` or `.env`.
- Avoid showing private organization data.
- Respect rate limits and pagination.
- Send a clear `User-Agent` in scripts.

---

## Search Repositories

```python
import requests

response = requests.get(
    "https://api.github.com/search/repositories",
    params={"q": "robotics language:python", "per_page": 5},
    headers={"User-Agent": "api-class-demo"},
    timeout=10,
)
response.raise_for_status()

data = response.json()
for repo in data["items"]:
    print(repo["full_name"], repo["stargazers_count"], repo["html_url"])
```

---

## Read Issues

```python
import requests

url = "https://api.github.com/repos/python/cpython/issues"
response = requests.get(url, params={"state": "open", "per_page": 5}, timeout=10)
response.raise_for_status()

for issue in response.json():
    print(issue["number"], issue["title"])
```

---

## Pagination

GitHub APIs often use pagination:

```python
params = {"per_page": 100, "page": 1}
```

Teach students to request small pages first and look at the `Link` response header.

---

## Optional Token from `.env`

```python
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_TOKEN")
headers = {"User-Agent": "api-class-demo"}
if token:
    headers["Authorization"] = f"Bearer {token}"
```

---

## Mini Projects

- Repository search dashboard.
- Issue tracker viewer.
- Top repositories by topic.
- Commit timeline for a public project.
- Compare stars/forks across frameworks.

---

## Best Practices

- Start unauthenticated with public data.
- Add authentication only when students understand secret handling.
- Cache repeated class queries.
- Show rate-limit headers.
- Keep write APIs out of beginner lessons.
