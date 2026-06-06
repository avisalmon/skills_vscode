---
name: Jokes and Trivia APIs
description: >
  Build fun beginner API demos with public joke and trivia endpoints: random jokes,
  quiz questions, categories, multiple-choice answers, HTML entity decoding, and
  safe classroom filtering. TRIGGER: joke API, trivia API, quiz API, Open Trivia,
  random joke, beginner API.
version: 1.0.0
category: Free API
tags: [api, jokes, trivia, quiz, beginner, json, teaching]
---

# Jokes and Trivia APIs

## Overview

Use this skill for quick, fun API demos. Joke and trivia APIs are great for showing request/response flow, randomization, and turning JSON into UI.

Example APIs:

- `https://official-joke-api.appspot.com/random_joke`
- `https://opentdb.com/api.php?amount=5&type=multiple`

---

## Security Check

- Public joke/trivia content can be unpredictable.
- Preview endpoints before class.
- Prefer safe categories and avoid offensive content where the API supports filters.
- Do not collect student names or scores unless needed.
- Decode HTML entities in trivia answers before display.

---

## Random Joke

```python
import requests

response = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=10)
response.raise_for_status()

joke = response.json()
print(joke["setup"])
print(joke["punchline"])
```

---

## Trivia Questions

```python
import html
import random
import requests

response = requests.get(
    "https://opentdb.com/api.php",
    params={"amount": 5, "type": "multiple"},
    timeout=10,
)
response.raise_for_status()

data = response.json()
for item in data["results"]:
    question = html.unescape(item["question"])
    answers = [html.unescape(item["correct_answer"])] + [html.unescape(a) for a in item["incorrect_answers"]]
    random.shuffle(answers)
    print(question)
    print(answers)
```

---

## Mini Projects

- Random joke button.
- Trivia quiz game.
- Score tracker.
- Category selector.
- Timed quiz round.

---

## Best Practices

- Add a content warning or preview data before class.
- Handle API rate limits.
- Decode HTML entities.
- Do not assume random content is always classroom-safe.
