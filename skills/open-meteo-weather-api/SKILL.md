---
name: Open-Meteo Weather API
description: >
  Teach students how to call a free weather API with no API key: current weather,
  hourly forecasts, daily forecasts, geocoding, units, time zones, JSON parsing,
  plotting, and error handling. TRIGGER: weather API, Open-Meteo, forecast,
  temperature, rain, wind, hourly weather, API lesson.
version: 1.0.0
category: Free API
tags: [api, weather, open-meteo, json, python, javascript, teaching]
---

# Open-Meteo Weather API

## Overview

Use this skill to teach basic REST API calls with a friendly real-world example: weather. Open-Meteo is excellent for students because simple forecast calls do not require registration or an API key for non-commercial/light usage.

Good lesson outcomes:

- Build a URL with query parameters.
- Send an HTTP GET request.
- Parse JSON.
- Read nested fields and arrays.
- Handle units, time zones, and missing values.
- Turn API data into a small app or chart.

Official docs: `https://open-meteo.com/en/docs`

---

## 1. First URL to Try

Tel Aviv current weather and hourly forecast:

```text
https://api.open-meteo.com/v1/forecast?latitude=32.0853&longitude=34.7818&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&hourly=temperature_2m,precipitation_probability&timezone=Asia/Jerusalem
```

Important parameters:

- `latitude`, `longitude`: WGS84 coordinates.
- `current`: current condition variables.
- `hourly`: time-series variables.
- `daily`: daily summary variables.
- `timezone`: use `Asia/Jerusalem` for Israel examples.
- `forecast_days`: number of forecast days, up to the service limit.

---

## 2. Python Example

```python
import requests

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 32.0853,
    "longitude": 34.7818,
    "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
    "hourly": "temperature_2m,precipitation_probability",
    "timezone": "Asia/Jerusalem",
}

response = requests.get(url, params=params, timeout=10)
response.raise_for_status()
data = response.json()

current = data["current"]
print("Temperature:", current["temperature_2m"], data["current_units"]["temperature_2m"])
print("Humidity:", current["relative_humidity_2m"], data["current_units"]["relative_humidity_2m"])
print("Wind:", current["wind_speed_10m"], data["current_units"]["wind_speed_10m"])
```

---

## 3. JavaScript Fetch Example

```javascript
const params = new URLSearchParams({
  latitude: '32.0853',
  longitude: '34.7818',
  current: 'temperature_2m,wind_speed_10m,weather_code',
  timezone: 'Asia/Jerusalem',
});

const response = await fetch(`https://api.open-meteo.com/v1/forecast?${params}`);
if (!response.ok) throw new Error(`HTTP ${response.status}`);

const data = await response.json();
console.log(data.current.temperature_2m, data.current_units.temperature_2m);
```

---

## 4. Weather Code Mapping

Open-Meteo returns WMO weather codes. For a simple classroom demo:

```python
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
}

code = data["current"]["weather_code"]
print(WEATHER_CODES.get(code, f"Unknown code {code}"))
```

---

## 5. Geocoding City Names

Open-Meteo also has a geocoding API:

```python
import requests

response = requests.get(
    "https://geocoding-api.open-meteo.com/v1/search",
    params={"name": "Haifa", "count": 5, "language": "en", "format": "json"},
    timeout=10,
)
response.raise_for_status()
results = response.json().get("results", [])

for place in results:
    print(place["name"], place.get("country"), place["latitude"], place["longitude"])
```

Class project idea: city search box -> forecast card.

---

## 6. Mini Projects

- Weather card for a selected city.
- Rain alert: print the next hour with precipitation probability above 50%.
- Temperature chart for the next 24 hours.
- Compare Tel Aviv, Jerusalem, Haifa, and Eilat.
- Solar/UV demo for outdoor robotics or sports planning.

---

## Teaching Notes

- Start with opening the URL in a browser so students see raw JSON.
- Then move to Python or JavaScript.
- Ask students to identify arrays, objects, units, and timestamps.
- Discuss API limits and respectful usage.
- Avoid polling every second; weather does not need high-frequency requests.
