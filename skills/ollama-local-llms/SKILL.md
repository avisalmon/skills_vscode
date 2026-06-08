---
name: ollama-local-llms
description: >
  Run large language models locally on your machine — zero API cost, fully
  offline, no data leaves your computer. Pull and chat with Llama, Gemma,
  Mistral, DeepSeek, Qwen, Phi and 100+ other models. Build Python apps
  using the Ollama REST API or ollama-python SDK. TRIGGER: user says
  "ollama", "local LLM", "run model locally", "offline AI", "private AI",
  "no API cost", "llama locally", "gemma local", or "local inference".
---

# Ollama — Local LLM Runner

> **Purpose**: Run 100+ open-source LLMs locally. Zero API cost, fully
> offline, private data never leaves the machine.

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Installation](#installation)
3. [Running Models](#running-models)
4. [Model Catalog](#model-catalog)
5. [REST API](#rest-api)
6. [Python SDK](#python-sdk)
7. [Embeddings](#embeddings)
8. [Modelfile — Custom Models](#modelfile--custom-models)
9. [Intel Proxy Setup](#intel-proxy-setup)
10. [Troubleshooting](#troubleshooting)
11. [Lessons Learned](#lessons-learned)

---

## Quick Reference

```powershell
# Install (Windows — paste in PowerShell)
irm https://ollama.com/install.ps1 | iex

# Pull a model
ollama pull gemma3          # 4B — fast, good quality
ollama pull llama3.2        # Meta 3B — great for chat
ollama pull phi4            # Microsoft 14B — strong reasoning
ollama pull qwen2.5-coder   # Best local coding model
ollama pull nomic-embed-text  # Embeddings

# Run interactive chat
ollama run gemma3
ollama run phi4

# List local models
ollama list

# Remove a model
ollama rm gemma3

# Check running server
ollama ps
```

---

## Installation

### Windows
```powershell
irm https://ollama.com/install.ps1 | iex
```
Or download installer: https://ollama.com/download/OllamaSetup.exe

Ollama runs as a background service on `http://localhost:11434`.

### Verify installation
```powershell
ollama --version
curl http://localhost:11434   # should return "Ollama is running"
```

---

## Running Models

### Interactive chat (terminal)
```powershell
ollama run llama3.2
# Type your message and press Enter
# /bye to exit
```

### One-shot (no interactive shell)
```powershell
ollama run gemma3 "Explain what a Docker container is in 2 sentences"
```

### Pass stdin
```powershell
Get-Content myfile.py | ollama run qwen2.5-coder "Review this Python code for bugs"
```

### With system prompt
```powershell
ollama run --system "You are a helpful Intel engineer." llama3.2
```

---

## Model Catalog

### Best general-purpose models (run on most hardware)

| Model | Size | Best For | Pull Command |
|-------|------|----------|--------------|
| `gemma3` | 4B | Fast chat, vision | `ollama pull gemma3` |
| `llama3.2` | 3B | Fast chat, tools | `ollama pull llama3.2` |
| `phi4` | 14B | Strong reasoning, math | `ollama pull phi4` |
| `mistral` | 7B | Balanced chat | `ollama pull mistral` |
| `llama3.1` | 8B | Best 8B model | `ollama pull llama3.1` |
| `qwen2.5` | 7B | Multilingual, 128K ctx | `ollama pull qwen2.5` |
| `deepseek-r1` | 8B | Reasoning / CoT | `ollama pull deepseek-r1` |

### Best coding models

| Model | Size | Pull Command |
|-------|------|-------------|
| `qwen2.5-coder` | 7B | `ollama pull qwen2.5-coder` |
| `deepseek-coder-v2` | 16B | `ollama pull deepseek-coder-v2` |
| `codellama` | 7B | `ollama pull codellama` |
| `phi4` | 14B | `ollama pull phi4` |

### Embedding models

| Model | Size | Pull Command |
|-------|------|-------------|
| `nomic-embed-text` | 274M | `ollama pull nomic-embed-text` |
| `mxbai-embed-large` | 335M | `ollama pull mxbai-embed-large` |
| `all-minilm` | 22M | `ollama pull all-minilm` |

### Vision models (image understanding)

| Model | Size | Pull Command |
|-------|------|-------------|
| `llava` | 7B | `ollama pull llava` |
| `gemma3` | 4B | `ollama pull gemma3` |
| `llama3.2-vision` | 11B | `ollama pull llama3.2-vision` |

---

## REST API

Ollama exposes an OpenAI-compatible REST API at `http://localhost:11434`.

### Chat completion (streaming)
```bash
curl http://localhost:11434/api/chat -d '{
  "model": "gemma3",
  "messages": [{"role": "user", "content": "Why is the sky blue?"}],
  "stream": false
}'
```

### Generate (raw)
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Write a haiku about silicon chips",
  "stream": false
}'
```

### List models
```bash
curl http://localhost:11434/api/tags
```

### Pull a model via API
```bash
curl http://localhost:11434/api/pull -d '{"name": "phi4"}'
```

### Embeddings
```bash
curl http://localhost:11434/api/embed -d '{
  "model": "nomic-embed-text",
  "input": "The quick brown fox"
}'
```

### OpenAI-compatible endpoint (drop-in replacement)
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"   # required but ignored
)

response = client.chat.completions.create(
    model="gemma3",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

---

## Python SDK

```powershell
pip install ollama
```

### Basic chat
```python
import ollama

response = ollama.chat(
    model="gemma3",
    messages=[{"role": "user", "content": "Explain recursion simply"}]
)
print(response.message.content)
```

### Streaming response
```python
import ollama

stream = ollama.chat(
    model="llama3.2",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)
for chunk in stream:
    print(chunk.message.content, end="", flush=True)
```

### With system prompt
```python
import ollama

response = ollama.chat(
    model="phi4",
    messages=[
        {"role": "system", "content": "You are a concise Python expert."},
        {"role": "user", "content": "What is a generator?"}
    ]
)
print(response.message.content)
```

### Multi-turn conversation
```python
import ollama

messages = [{"role": "system", "content": "You are a helpful assistant."}]

while True:
    user_input = input("You: ")
    if user_input.lower() in ("/bye", "exit", "quit"):
        break

    messages.append({"role": "user", "content": user_input})
    response = ollama.chat(model="gemma3", messages=messages)
    assistant_msg = response.message.content
    messages.append({"role": "assistant", "content": assistant_msg})
    print(f"AI: {assistant_msg}\n")
```

### Generate (raw, no conversation)
```python
import ollama

response = ollama.generate(
    model="llama3.2",
    prompt="List 5 Python best practices"
)
print(response.response)
```

### Embeddings
```python
import ollama

result = ollama.embed(
    model="nomic-embed-text",
    input="The quick brown fox jumps over the lazy dog"
)
print(result.embeddings[0][:5])   # first 5 dimensions
```

### List / pull / delete models
```python
import ollama

# List locally available models
models = ollama.list()
for m in models.models:
    print(m.model, m.size)

# Pull a model
ollama.pull("phi4")

# Delete a model
ollama.delete("phi4")
```

---

## Embeddings

Use Ollama embeddings for RAG, semantic search, and similarity.

```python
import ollama
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

texts = [
    "Python is a programming language",
    "Django is a Python web framework",
    "The cat sat on the mat",
]

embeddings = [
    ollama.embed(model="nomic-embed-text", input=t).embeddings[0]
    for t in texts
]

# Compare first two (both about Python) vs third
print(cosine_similarity(embeddings[0], embeddings[1]))  # high ~0.9
print(cosine_similarity(embeddings[0], embeddings[2]))  # low ~0.4
```

---

## Modelfile — Custom Models

Create a `Modelfile` to customize any base model:

```dockerfile
FROM llama3.2

# Set system prompt
SYSTEM "You are an expert Intel chip engineer. Answer only about semiconductor topics."

# Tune temperature (0=deterministic, 1=creative)
PARAMETER temperature 0.3

# Context window size
PARAMETER num_ctx 8192

# Stop tokens
PARAMETER stop "<|end|>"
```

```powershell
# Build and name your custom model
ollama create intel-expert -f Modelfile

# Run it
ollama run intel-expert "What is the difference between 3nm and 2nm process nodes?"
```

---

## Intel Proxy Setup

Ollama downloads models from `ollama.com`. On Intel corporate network, the proxy
is required.

### Set proxy for model downloads (Windows)
```powershell
$env:HTTPS_PROXY = "http://proxy-iil.intel.com:912"
$env:HTTP_PROXY  = "http://proxy-iil.intel.com:912"
ollama pull gemma3
```

### Permanent (user environment variable)
```powershell
[System.Environment]::SetEnvironmentVariable("HTTPS_PROXY", "http://proxy-iil.intel.com:912", "User")
[System.Environment]::SetEnvironmentVariable("HTTP_PROXY",  "http://proxy-iil.intel.com:912", "User")
```

> **Note**: Once models are downloaded they run entirely offline. The proxy is
> only needed for `ollama pull`.

---

## Troubleshooting

### "connection refused" — server not running
```powershell
# Start the Ollama server manually
ollama serve
```

### Model download fails (proxy issue on Intel network)
```powershell
$env:HTTPS_PROXY = "http://proxy-iil.intel.com:912"
ollama pull gemma3
```

### Out of memory (model too large)
- Use a smaller quantized variant: `ollama pull llama3.1:8b-instruct-q4_0`
- Check available VRAM: `nvidia-smi` or use CPU-only models like `phi4-mini`

### Slow responses (running on CPU)
- CPU inference is 10-30x slower than GPU
- Use smaller models: `phi4-mini` (3.8B), `llama3.2` (3B), `gemma3` (1B)
- Install CUDA drivers to enable GPU acceleration

### Check which GPU is being used
```powershell
ollama ps   # shows model + hardware (CPU/GPU/VRAM used)
```

---

## Lessons Learned

- **Model sizes**: 3-8B models run fine on CPU (slow but usable). 14B+ need
  a GPU for reasonable speed.
- **Best small model 2026**: `gemma3` (4B) or `llama3.2` (3B) for general use;
  `phi4-mini` (3.8B) for reasoning.
- **Best coding model**: `qwen2.5-coder:7b` consistently outperforms `codellama`.
- **Embeddings**: `nomic-embed-text` is the standard choice for RAG pipelines.
- **Privacy**: Once downloaded, models run 100% offline. No data sent to any
  server. Safe for sensitive Intel internal data.
- **OpenAI drop-in**: Use `base_url="http://localhost:11434/v1"` with the
  `openai` Python package — no code changes needed.
- **Context window**: Default is 2K tokens for most models. Set
  `PARAMETER num_ctx 8192` in a Modelfile to increase it.
- **Proxy**: Only needed for `ollama pull`. Not needed for inference.
