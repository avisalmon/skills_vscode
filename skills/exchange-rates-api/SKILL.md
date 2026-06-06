---
name: Exchange Rates API
description: >
  Use free exchange-rate APIs for currency conversion demos: latest rates,
  historical rates, base currencies, calculations, caching, precision, and
  finance-data disclaimers. TRIGGER: exchange rate API, currency API, FX rates,
  currency converter, EUR USD, ILS.
version: 1.0.0
category: Free API
tags: [api, currency, exchange-rates, finance, json, teaching]
---

# Exchange Rates API

## Overview

Use this skill to teach APIs with currency conversion. A good free classroom endpoint is Frankfurter, which is based on European Central Bank reference data.

Docs: `https://www.frankfurter.app/docs/`

---

## Security Check

- No key needed for Frankfurter.
- Use for education, not trading or financial advice.
- Rates may not be realtime.
- Cache responses in class.
- Handle unsupported currencies.
- Use decimal-aware calculations for serious money apps.

---

## Latest Rates

```python
import requests

response = requests.get(
    "https://api.frankfurter.app/latest",
    params={"from": "EUR", "to": "USD,ILS,GBP"},
    timeout=10,
)
response.raise_for_status()

data = response.json()
print(data["date"])
print(data["rates"])
```

---

## Convert Amount

```python
amount = 100
response = requests.get(
    "https://api.frankfurter.app/latest",
    params={"amount": amount, "from": "USD", "to": "ILS"},
    timeout=10,
)
response.raise_for_status()
print(response.json())
```

---

## Historical Rate

```python
response = requests.get(
    "https://api.frankfurter.app/2024-01-01",
    params={"from": "EUR", "to": "USD"},
    timeout=10,
)
response.raise_for_status()
print(response.json())
```

---

## Mini Projects

- Currency converter.
- Travel budget calculator.
- Historical exchange-rate chart.
- Compare currencies over time.
- Alert when rate crosses a threshold.

---

## Best Practices

- Show the date of the rate.
- Do not call it realtime unless the provider says so.
- Validate currency codes.
- Keep finance disclaimers visible.
