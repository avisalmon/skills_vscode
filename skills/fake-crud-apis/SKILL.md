---
name: Fake CRUD APIs
description: >
  Practice GET, POST, PUT, PATCH, and DELETE with safe fake APIs such as
  JSONPlaceholder and DummyJSON. Learn REST resources, request bodies, headers,
  status codes, forms, product carts, and mock backends. TRIGGER: JSONPlaceholder,
  DummyJSON, fake API, CRUD API, POST request, REST practice.
version: 1.0.0
category: Free API
tags: [api, crud, jsonplaceholder, dummyjson, rest, forms, teaching]
---

# Fake CRUD APIs

## Overview

Use this skill to teach REST operations without risking real data. JSONPlaceholder and DummyJSON provide fake users, posts, comments, products, carts, and auth-like examples.

Docs:

- `https://jsonplaceholder.typicode.com/`
- `https://dummyjson.com/`

---

## Security Check

- Use fake data only.
- Do not submit real passwords or personal data.
- Explain that POST/PUT responses are simulated and may not persist.
- Keep fake credentials fake.
- Do not teach students to trust mock APIs as production systems.

---

## GET Posts

```python
import requests

response = requests.get("https://jsonplaceholder.typicode.com/posts", timeout=10)
response.raise_for_status()

for post in response.json()[:5]:
    print(post["id"], post["title"])
```

---

## POST a Fake Resource

```python
import requests

response = requests.post(
    "https://jsonplaceholder.typicode.com/posts",
    json={"title": "API class", "body": "Hello REST", "userId": 1},
    timeout=10,
)
response.raise_for_status()
print(response.status_code, response.json())
```

---

## DummyJSON Products

```python
import requests

response = requests.get("https://dummyjson.com/products/search", params={"q": "phone"}, timeout=10)
response.raise_for_status()

for product in response.json()["products"][:5]:
    print(product["title"], product["price"])
```

---

## Mini Projects

- Blog post dashboard.
- Product search page.
- Shopping cart mockup.
- Form that sends POST.
- REST status-code lab.

---

## Best Practices

- Inspect status codes.
- Compare GET vs POST in browser/devtools.
- Validate form input before sending.
- Make clear which writes are simulated.
