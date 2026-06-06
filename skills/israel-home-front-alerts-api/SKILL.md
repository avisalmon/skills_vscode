---
name: Israel Home Front Alerts Data
description: >
  Teach API design and emergency-data responsibility using Israel Home Front
  Command alert information: official sources, safe mock data, JSON schemas,
  polling discipline, location filtering, and classroom simulations. TRIGGER:
  Pikud HaOref, Home Front Command, Israel alerts, emergency alerts, siren,
  פיקוד העורף, התרעות.
version: 1.0.0
category: Free API
tags: [api, israel, emergency, alerts, json, teaching, safety]
---

# Israel Home Front Alerts Data

## Overview

Use this skill to teach API consumption with emergency alert data as the domain. This is a powerful classroom example because the data shape is simple, but the engineering responsibility is serious.

Important: do not teach students to depend on unofficial endpoints for life-safety decisions. For real alerts, users must use official Home Front Command channels such as the official website, app, sirens, radio, and official messages.

Official site: `https://www.oref.org.il/`

---

## 1. Safety Rules

For this topic, start the lesson with these rules:

- This is an API/data-format lesson, not a life-safety system.
- Do not scrape, overload, or reverse-engineer emergency systems in class.
- Do not build apps that claim to replace official alerts.
- Use mock JSON for coding exercises.
- If using any public/community endpoint for demonstration, label it as unofficial and unstable.
- Cache and poll slowly. Emergency systems are not toys.

---

## 2. Recommended Classroom Approach

Use official public information as context, then teach with local mock data.

Create `alerts-sample.json`:

```json
{
  "alerts": [
    {
      "id": "demo-001",
      "time": "2026-06-06T12:30:00+03:00",
      "category": "rocket_alert",
      "area": "Dan",
      "cities": ["Tel Aviv", "Ramat Gan", "Givatayim"],
      "instructions": "Enter protected space according to official guidance.",
      "source": "classroom-demo"
    }
  ]
}
```

Then teach the same operations students would use with a real API:

- fetch JSON
- validate fields
- filter by city
- sort by time
- show active alerts
- handle empty results
- handle network errors

---

## 3. Python Mock Client

```python
import json
from pathlib import Path

CITY = "Tel Aviv"

data = json.loads(Path("alerts-sample.json").read_text(encoding="utf-8"))
alerts = data.get("alerts", [])

matching = [alert for alert in alerts if CITY in alert.get("cities", [])]

if not matching:
    print(f"No demo alerts for {CITY}")
else:
    for alert in matching:
        print(alert["time"], alert["area"], alert["instructions"])
```

---

## 4. JavaScript Mock Client

```javascript
async function loadAlerts(city) {
  const response = await fetch('./alerts-sample.json');
  if (!response.ok) throw new Error(`HTTP ${response.status}`);

  const data = await response.json();
  return (data.alerts || []).filter(alert => (alert.cities || []).includes(city));
}

const alerts = await loadAlerts('Tel Aviv');
console.log(alerts);
```

---

## 5. Schema Validation Discussion

Emergency data should be validated before display.

Minimum fields:

```text
id: string
time: ISO 8601 timestamp
category: string
area: string
cities: list of strings
instructions: string
source: string
```

Questions for students:

- What happens if `cities` is missing?
- What happens if the timestamp is invalid?
- Should duplicate alerts be shown twice?
- How do we separate active alerts from history?
- How do we avoid panic from stale data?

---

## 6. Polling Pattern

If you demonstrate polling with mock or approved data:

```javascript
const POLL_MS = 30000;

async function refresh() {
  try {
    const alerts = await loadAlerts('Tel Aviv');
    renderAlerts(alerts);
  } catch (error) {
    renderStatus('Could not load alerts. Check official sources.');
  }
}

refresh();
setInterval(refresh, POLL_MS);
```

Teaching point: polling too often is bad engineering. It wastes bandwidth and can stress services.

---

## 7. Mini Projects

- Build a mock alert dashboard.
- Add a city filter.
- Deduplicate alerts by `id`.
- Add stale-data warning if the newest alert is older than a threshold.
- Add tests for malformed JSON.
- Build a simulator that appends a new mock alert every minute.

---

## Best Practices

- Use official sources for real-world emergency information.
- Use mock data for coding lessons.
- Display timestamps and source labels clearly.
- Handle empty states calmly.
- Never hide uncertainty in emergency-related data.
- Never claim a student project is an official alert system.
