---
name: Israel Public Transport GTFS API
description: >
  Teach public transport data APIs using GTFS and GTFS-Realtime: stops, routes,
  trips, stop times, train/bus planning, delays, service alerts, vehicle positions,
  and Israel transit datasets. TRIGGER: Israel train API, public transport API,
  GTFS, GTFS realtime, train schedule, bus schedule, transit data.
version: 1.0.0
category: Free API
tags: [api, israel, transport, gtfs, trains, buses, realtime, data]
---

# Israel Public Transport GTFS API

## Overview

Use this skill to teach API/data work with public transport. GTFS is an open standard used by transit agencies to publish routes, stops, trips, schedules, and realtime updates.

This is excellent for students because it combines practical data engineering with a familiar question: when is the next train or bus?

GTFS docs: `https://gtfs.org/documentation/overview/`

---

## 1. What GTFS Contains

GTFS Schedule is usually a ZIP file with text files such as:

```text
agency.txt
routes.txt
trips.txt
stops.txt
stop_times.txt
calendar.txt
calendar_dates.txt
```

Some feeds omit optional files. For example, a feed may include `calendar.txt` but not `calendar_dates.txt`. Treat optional files as optional in code.

Core relationships:

```text
route -> trip -> stop_times -> stop
```

GTFS-Realtime can add:

- trip updates: delays and changed times
- service alerts: disruptions and station/route notices
- vehicle positions: where vehicles are now

---

## 2. Data Setup

Python packages:

```bash
pip install pandas requests gtfs-realtime-bindings
```

For a first lesson, start with static GTFS because it is plain CSV inside a ZIP.

```python
import zipfile
import pandas as pd
from pathlib import Path

feed_zip = Path("gtfs.zip")
extract_dir = Path("gtfs")

with zipfile.ZipFile(feed_zip) as zf:
    zf.extractall(extract_dir)

stops = pd.read_csv(extract_dir / "stops.txt")
routes = pd.read_csv(extract_dir / "routes.txt")
trips = pd.read_csv(extract_dir / "trips.txt")
stop_times = pd.read_csv(extract_dir / "stop_times.txt")
calendar_dates_path = extract_dir / "calendar_dates.txt"
calendar_dates = pd.read_csv(calendar_dates_path) if calendar_dates_path.exists() else pd.DataFrame()

print(stops.head())
print(routes.head())
```

Israel train station examples from the public GTFS feed:

```text
37376  חוף הכרמל / Carmel Beach
37358  תל אביב מרכז / Tel Aviv Center / Savidor
37350  השלום / Tel Aviv Hashalom
37292  תל אביב ההגנה / Tel Aviv Haganah
37360  תא אוניברסיטה / Tel Aviv University
```

The feed may store Hebrew names in `stops.txt` and English names in `translations.txt`, so robust code should either join translations or match known stop IDs.

---

## 3. Find Stations by Name

```python
query = "Tel Aviv"
matching_stops = stops[stops["stop_name"].str.contains(query, case=False, na=False)]
print(matching_stops[["stop_id", "stop_name", "stop_lat", "stop_lon"]].head(20))
```

If English search does not work, load `translations.txt` and join it by `trans_id == stop_name`.

Class exercise: change the query to find a station near home or school.

---

## 4. Next Departures from a Stop

```python
stop_id = matching_stops.iloc[0]["stop_id"]

departures = stop_times[stop_times["stop_id"].astype(str) == str(stop_id)]
departures = departures.sort_values("departure_time")

print(departures[["trip_id", "departure_time", "stop_sequence"]].head(20))
```

Join with route names:

```python
trip_routes = trips.merge(routes, on="route_id", how="left")
full = departures.merge(trip_routes, on="trip_id", how="left")

print(full[["departure_time", "route_short_name", "route_long_name", "trip_id"]].head(20))
```

---

## 5. GTFS-Realtime Concept

GTFS-Realtime uses Protocol Buffers instead of normal JSON. That is a great teaching moment: not all APIs return JSON.

```python
import requests
from google.transit import gtfs_realtime_pb2

url = "PUT_OFFICIAL_GTFS_REALTIME_URL_HERE"
response = requests.get(url, timeout=15)
response.raise_for_status()

feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(response.content)

for entity in feed.entity[:5]:
    print(entity.id)
    if entity.HasField("trip_update"):
        print("trip update", entity.trip_update.trip.trip_id)
    if entity.HasField("alert"):
        print("service alert")
    if entity.HasField("vehicle"):
        print("vehicle position")
```

Use the official data portal or agency documentation for the actual feed URL and terms.

---

## 6. Good Student Projects

- Station search.
- Next departures board.
- Route explorer.
- Map stops using latitude/longitude.
- Delay dashboard using GTFS-Realtime.
- Compare planned departure time and realtime delay.
- Service alert viewer.

---

## 7. Data Quality Questions

Ask students:

- What if a trip runs after midnight and time is `25:10:00`?
- What if a station name appears in Hebrew and English?
- What if a train is cancelled?
- What if realtime data is temporarily unavailable?
- What should the UI show when data is stale?

---

## Best Practices

- Keep raw downloaded feeds separate from parsed outputs.
- Use official data portals and respect terms of use.
- Cache static GTFS locally during class.
- Do not hammer realtime feeds.
- Validate required files before parsing.
- Treat schedule and realtime data as separate layers.
- Always show last-updated time in dashboards.
