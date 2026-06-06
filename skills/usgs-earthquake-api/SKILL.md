---
name: USGS Earthquake API
description: >
  Use USGS earthquake feeds for map and data projects: GeoJSON, magnitude,
  location, time, recent earthquakes, bounding boxes, plotting, and alert-style
  dashboards. TRIGGER: earthquake API, USGS API, GeoJSON, earthquake map,
  magnitude, seismic data.
version: 1.0.0
category: Free API
tags: [api, earthquake, usgs, geojson, maps, science, teaching]
---

# USGS Earthquake API

## Overview

Use this skill to teach geospatial APIs with live science data. USGS earthquake feeds return GeoJSON, making them excellent for map projects.

Docs: `https://earthquake.usgs.gov/fdsnws/event/1/`

---

## Security Check

- No key needed.
- Data is public science data.
- Do not present classroom dashboards as emergency warning systems.
- Cache repeated requests.
- Handle empty result sets.
- Show source and timestamp.

---

## Recent Earthquakes Feed

```python
import datetime as dt
import requests

response = requests.get(
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson",
    timeout=10,
)
response.raise_for_status()

data = response.json()
for feature in data["features"][:5]:
    props = feature["properties"]
    lon, lat, depth = feature["geometry"]["coordinates"]
    time = dt.datetime.fromtimestamp(props["time"] / 1000, tz=dt.timezone.utc)
    print(props["mag"], props["place"], lat, lon, time)
```

---

## Query by Bounding Box

```python
import requests

response = requests.get(
    "https://earthquake.usgs.gov/fdsnws/event/1/query",
    params={
        "format": "geojson",
        "starttime": "2026-01-01",
        "endtime": "2026-01-31",
        "minmagnitude": 4,
        "minlatitude": 29,
        "maxlatitude": 34,
        "minlongitude": 34,
        "maxlongitude": 36,
    },
    timeout=10,
)
response.raise_for_status()
print(response.json()["metadata"]["count"])
```

---

## Mini Projects

- Recent earthquake map.
- Magnitude histogram.
- Filter by region.
- Alert-style dashboard with clear disclaimer.
- Compare earthquakes by day.

---

## Best Practices

- Learn GeoJSON: `features`, `geometry`, `properties`.
- Convert epoch milliseconds to readable time.
- Do not over-poll feeds.
- Label units and timestamps.
