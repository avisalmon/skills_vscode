---
name: PokéAPI
description: >
  Use the free PokéAPI for fun JSON lessons: Pokémon data, abilities, sprites,
  types, nested resources, linked URLs, arrays, images, and small search apps.
  TRIGGER: PokéAPI, Pokemon API, sprites, abilities, types, beginner API.
version: 1.0.0
category: Free API
tags: [api, pokemon, json, images, beginner, teaching]
---

# PokéAPI

## Overview

Use this skill for a very friendly first API project. PokéAPI is free, public, no key required, and returns nested JSON that is fun to explore.

Docs: `https://pokeapi.co/`

---

## Security Check

- No API key needed.
- No personal data involved.
- Cache during class if many students hit the same endpoint.
- Do not spam the API in loops.
- Validate user input before building URLs.

---

## First Call

```python
import requests

name = "pikachu"
response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name}", timeout=10)
response.raise_for_status()

data = response.json()
print(data["name"])
print(data["height"], data["weight"])
print([t["type"]["name"] for t in data["types"]])
print(data["sprites"]["front_default"])
```

---

## Browser Fetch

```javascript
const response = await fetch('https://pokeapi.co/api/v2/pokemon/pikachu');
const pokemon = await response.json();

console.log(pokemon.name);
console.log(pokemon.types.map(item => item.type.name));
console.log(pokemon.sprites.front_default);
```

---

## Mini Projects

- Pokémon search card.
- Type filter.
- Random Pokémon button.
- Guess-the-sprite game.
- Compare height and weight chart.
- Follow linked URLs to abilities and species.

---

## Best Practices

- Lowercase names before lookup.
- Handle 404 for unknown Pokémon.
- Teach nested arrays using `types` and `abilities`.
- Show image rendering with `sprites.front_default`.
