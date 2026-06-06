---
name: OpenAI API Setup and Cost Tracking
description: >
  Guide users through OpenAI API setup: create an account, generate an API key,
  store it in .env, call chat/model APIs from Python, list available models,
  estimate token costs, read usage/cost dashboards, and avoid leaking keys.
  TRIGGER: OpenAI API, API key, .env, chat completions, responses API, model list,
  token cost, usage dashboard.
version: 1.0.0
category: API
tags: [api, openai, ai, dotenv, python, cost, tokens, security]
---

# OpenAI API Setup and Cost Tracking

## Overview

Use this skill when teaching or building a first OpenAI API integration. It guides the user through account setup, key storage, first API call, model discovery, and cost awareness.

OpenAI is a paid/key-based API. Do not present it as a free public API. Always teach key safety before the first request.

---

## 1. Register and Create an API Key

High-level steps:

1. Go to the OpenAI platform website.
2. Create or sign in to an account.
3. Set up billing if required.
4. Open the API keys page.
5. Create a new secret key.
6. Copy it once and store it safely.

Important safety rules:

- Never paste an API key into code.
- Never commit an API key to git.
- Never share screenshots containing keys.
- If a key leaks, revoke it immediately and create a new one.

---

## 2. Store the Key in `.env`

Create a local `.env` file in your project:

```text
OPENAI_API_KEY=replace_with_your_real_key
```

Make sure `.env` is in `.gitignore`:

```text
.env
.env.*
!.env.example
```

Create a safe `.env.example` for students:

```text
OPENAI_API_KEY=your_key_here
```

---

## 3. Install Python Packages

```bash
pip install openai python-dotenv
```

---

## 4. First Python Call

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

response = client.responses.create(
    model="gpt-4.1-mini",
    input="Explain APIs to a high-school robotics student in 3 sentences.",
)

print(response.output_text)
```

If the SDK version changes, check the current OpenAI Python SDK docs and update the call shape.

---

## 5. List Available Models

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

models = client.models.list()
for model in models.data[:20]:
    print(model.id)
```

Use this to show students that APIs can expose service metadata, not only task output.

---

## 6. Token and Cost Awareness

Teach this before running loops.

Cost usually depends on:

- model name
- input tokens
- output tokens
- cached input tokens, if applicable
- extra tools or modalities, if used

Basic habits:

- Use small prompts during development.
- Limit output length when possible.
- Avoid accidental loops.
- Log request count and approximate token usage.
- Check the provider's pricing page before demos.

Example usage logging:

```python
response = client.responses.create(
    model="gpt-4.1-mini",
    input="Give me one API lesson idea.",
)

print(response.output_text)
if getattr(response, "usage", None):
    print(response.usage)
```

---

## 7. Usage and Cost Data

For real billing/cost data, use the official platform dashboard or documented usage/cost endpoints available to the account.

Classroom workflow:

1. Show the pricing page before running code.
2. Run one request.
3. Inspect returned usage metadata if available.
4. Check the platform usage/cost dashboard.
5. Estimate cost before scaling to many requests.

Do not hardcode pricing numbers in long-lived course material. Pricing changes.

---

## 8. Safe Helper Function

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY. Put it in .env and keep .env out of git.")
    return OpenAI(api_key=api_key)
```

---

## 9. Classroom Exercises

- Ask the model to summarize weather JSON.
- Generate a friendly explanation from a train schedule result.
- Build a simple chatbot with a strict system prompt.
- Compare short vs long prompts and inspect token usage.
- Add a monthly budget warning in your app configuration.

---

## Best Practices

- Keep `.env` local and ignored by git.
- Use `.env.example` for templates.
- Revoke leaked keys immediately.
- Put cost checks before loops and batch jobs.
- Log request count during demos.
- Use the smallest capable model for classroom experiments.
- Do not store student API keys on a shared machine.
