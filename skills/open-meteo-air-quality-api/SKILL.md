---
name: Open-Meteo Air Quality API
description: >
  Use Open-Meteo's free air-quality API for environmental data projects: PM2.5,
  PM10, ozone, nitrogen dioxide, European AQI, hourly forecasts, charts, health
  disclaimers, and city comparisons. TRIGGER: air quality API, AQI, PM2.5,
  pollution API, Open-Meteo air quality.
version: 1.0.0
category: Free API
tags: [api, air-quality, open-meteo, environment, aqi, json, teaching]
---

# Open-Meteo Air Quality API

## Overview

Use this skill to extend weather API lessons into environmental data. Open-Meteo provides air-quality forecasts with no key for light/non-commercial use.

Docs: `https://open-meteo.com/en/docs/air-quality-api`

---

## Security Check

- No key needed for light/non-commercial use.
- Do not provide medical advice.
- Show source, units, and timestamp.
- Avoid over-polling.
- Use health disclaimers for AQI-related displays.

---

## First Call

```python
import requests

response = requests.get(
    "https://air-quality-api.open-meteo.com/v1/air-quality",
    params={
        "latitude": 32.0853,
        "longitude": 34.7818,
        "hourly": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone,european_aqi",
        "timezone": "Asia/Jerusalem",
    },
    timeout=10,
)
response.raise_for_status()

data = response.json()
print(data["hourly"]["time"][:3])
print(data["hourly"]["pm2_5"][:3])
```

---

## Find Worst Hour

```python
hourly = data["hourly"]
values = list(zip(hourly["time"], hourly["european_aqi"]))
values = [(time, aqi) for time, aqi in values if aqi is not None]
worst_time, worst_aqi = max(values, key=lambda item: item[1])
print(worst_time, worst_aqi)
```

---

## Mini Projects

- Air-quality card for a city.
- PM2.5 chart.
- Compare Tel Aviv, Haifa, Jerusalem, and Eilat.
- Simple outdoor-activity advisory with disclaimer.
- Combine geocoding -> air-quality lookup.

---

## Best Practices

- Label units clearly.
- Use a disclaimer: informational, not medical advice.
- Handle missing values.
- Avoid scary UI language.
- Cache repeated class queries.
