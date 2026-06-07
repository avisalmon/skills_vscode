---
name: Whatsapp Api Messaging
description: >
  WhatsApp API integration via whatsapp-web.js.
---

# Whatsapp Api Messaging

## 📱 WhatsApp API Integration (whatsapp-web.js)

> **For AI Assistant**: Use this guide to send/receive WhatsApp messages from Python, integrate with periodic tasks, and manage the WhatsApp API server.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Server Setup](#server-setup)
4. [Python Client](#python-client)
5. [API Reference](#api-reference)
6. [Periodic Scheduler Integration](#periodic-scheduler-integration)
7. [Bot Development](#bot-development)
8. [Session Management](#session-management)
9. [Troubleshooting](#troubleshooting)

---

## Overview

WhatsApp messaging is available via a local **Node.js REST API server** that wraps [whatsapp-web.js](https://github.com/nicholasjorge/whatsapp-web.js). Python code communicates with it over HTTP on `localhost:3100`.

### Capabilities

| Feature | Supported |
|---------|-----------|
| Send text messages | ✅ |
| Send media (images, PDFs, docs) | ✅ |
| Receive incoming messages | ✅ |
| List all chats | ✅ |
| Read chat history | ✅ |
| Detect unanswered chats | ✅ |
| Auto-reply bots | ✅ |
| Group messages | ✅ |
| Task failure notifications | ✅ |
| Headless (no browser popups) | ✅ |
| Session persistence (no re-scan) | ✅ |

---

## Architecture

```
┌──────────────────┐       HTTP        ┌───────────────────┐      WebSocket     ┌──────────────┐
│  Python           │  ──────────────▶ │  Node.js Server    │  ────────────────▶ │  WhatsApp    │
│  (periodic, etc.) │  localhost:3100   │  (whatsapp-web.js) │   via Puppeteer    │  Web Servers │
└──────────────────┘                   └───────────────────┘                    └──────────────┘
                                              │
                                       .wwebjs_auth/
                                       (session saved)
```

**Key paths:**

| Component | Location |
|-----------|----------|
| Node.js server | `C:\DELETE LATER\NVIDIACAGGLE\whatsapp-api\server.js` |
| Python module (periodic) | `periodic/whatsapp.py` |
| Session data | `C:\DELETE LATER\NVIDIACAGGLE\whatsapp-api\.wwebjs_auth/` |

---

## Server Setup

### Prerequisites

- **Node.js** ≥ 18 (`node --version`)
- **npm** (`npm --version`)

### First-Time Setup

```powershell
cd "C:\DELETE LATER\NVIDIACAGGLE\whatsapp-api"
npm install
npx puppeteer browsers install chrome   # required — installs Chromium for Puppeteer
node server.js
```

On first run:
1. A **QR code** appears in the terminal (also saved as `qr_code.png` and opened automatically)
2. Open WhatsApp on your phone → **Settings → Linked Devices → Link a Device**
3. Scan the QR code
4. Terminal shows: `✓ Authenticated` → `✓ WhatsApp client ready!`

### Subsequent Runs

```powershell
cd "C:\DELETE LATER\NVIDIACAGGLE\whatsapp-api"
node server.js
```

No QR scan needed — session is persisted in `.wwebjs_auth/`.

### Running as Background Process

```powershell
# PowerShell — run in background
Start-Process -NoNewWindow -FilePath "node" -ArgumentList "server.js" `
    -WorkingDirectory "C:\DELETE LATER\NVIDIACAGGLE\whatsapp-api"
```

---

## Python Client

### From `periodic` package (recommended)

```python
from periodic.whatsapp import WhatsAppClient, send_whatsapp_message

# Full client
wa = WhatsAppClient()
wa.send("+972547885798", "Hello from Python! 🐍")
wa.send_media("+972547885798", r"C:\path\to\file.pdf", caption="Report attached")

print(wa.is_ready())         # True/False
print(wa.get_chats())        # List of all chats
print(wa.get_messages())     # Recent incoming messages
print(wa.get_chat_history("+972547885798"))  # Chat history

# Quick one-liner
send_whatsapp_message("+972547885798", "Quick message!")
```

### From standalone script

```python
# Uses: DELETE LATER/whatsapp_experiment/whatsapp_client.py
import sys; sys.path.insert(0, r"C:\Projects\Swarmer\DELETE LATER\whatsapp_experiment")
from whatsapp_client import WhatsAppClient

wa = WhatsAppClient()
wa.send("+972547885798", "Hello!")
```

---

## API Reference

The Node.js server exposes these HTTP endpoints on `http://localhost:3100`:

### `GET /status`

Check if the WhatsApp client is connected.

```json
{"ready": true, "uptime": 1234.5, "storedMessages": 7}
```

### `POST /send`

Send a text message.

```json
// Request
{"phone": "+972547885798", "message": "Hello!"}

// Response
{"success": true, "to": "972547885798@c.us", "messageId": "...", "timestamp": 1234567890}
```

### `POST /send-media`

Send a file (image, PDF, etc.).

```json
// Request
{"phone": "+972547885798", "mediaPath": "C:\\path\\to\\file.png", "caption": "Optional caption"}
```

### `GET /chats?limit=30`

List all conversations with last message info.

```json
[
  {
    "id": "972547885798@c.us",
    "name": "Contact Name",
    "isGroup": false,
    "unreadCount": 2,
    "lastMessage": {"body": "...", "timestamp": 1234567890, "fromMe": false}
  }
]
```

### `GET /chat-history/:phone?limit=50`

Fetch message history for a specific chat.

```json
[
  {
    "from": "972547885798@c.us",
    "body": "Hello",
    "timestamp": 1234567890,
    "date": "2026-02-14T17:00:00.000Z",
    "fromMe": false,
    "type": "chat",
    "hasMedia": false
  }
]
```

### `GET /messages?limit=20`

Get incoming messages buffered since server started.

### `GET /messages/:phone?limit=20`

Get incoming messages from a specific number.

### `GET /chat-by-name?name=NAME&q=QUERY&limit=50`

Search a chat by contact name. Supports `@lid` chats (new WhatsApp format). Returns messages matching query `q` via `client.searchMessages()`.

- `name` (required): Contact/chat name (supports Hebrew, URL-encoded)
- `q` (optional): text to search within the chat (e.g. `youtu` for YouTube links)
- `limit` (optional): max results, default 50

Prefers exact name match, falls back to partial match.

```json
// Response
{
  "chatName": "שרון",
  "chatId": "268611734245389@lid",
  "messageCount": 14,
  "messages": [
    {"id": "...", "from": "...", "body": "https://youtu.be/...", "date": "2026-03-21T...", "fromMe": false, ...}
  ]
}
```

---

## Critical Lessons Learned (Apr 2026)

### @lid vs @c.us Chat IDs

WhatsApp now uses **`@lid`** format for many chats (e.g. `268611734245389@lid`) instead of the traditional `@c.us` (phone-based).

- `GET /chats` returns both formats in the `id` field
- `getChatById()` does **NOT** work with `@lid` IDs — throws `waitForChatLoading` error
- `chat.fetchMessages()` also fails on `@lid` chats with the same error
- **Working approach**: Use `client.getChats()` to find chat by name, then `client.searchMessages(query, {chatId: ...})` to search within it
- The `/chat-by-name` endpoint handles this correctly

### Puppeteer Chrome Version

- After clearing `.wwebjs_auth/` or on fresh install, run `npx puppeteer browsers install chrome`
- If the server hangs at "Initializing WhatsApp client..." forever, the Puppeteer Chrome is missing or outdated
- Chrome version must match what Puppeteer expects (check error message for required version)

### Session Stale After Chrome Update

- If the session was created with an older Puppeteer Chrome and you install a new one, the session becomes stale
- Server starts but never becomes `ready` — stuck at "Initializing WhatsApp client..."
- **Fix**: Delete `.wwebjs_auth/`, restart server, re-scan QR code
- To delete: must kill both `node` and `chrome` processes first (Chrome holds file locks)

```powershell
Stop-Process -Name node -Force -ErrorAction SilentlyContinue
Stop-Process -Name chrome -Force -ErrorAction SilentlyContinue
Remove-Item "C:\DELETE LATER\NVIDIACAGGLE\whatsapp-api\.wwebjs_auth" -Recurse -Force
```

### Corporate Proxy blocks localhost

- Corporate HTTP proxy intercepts `localhost` requests and returns 403
- **Python**: Use `requests.Session()` with `session.trust_env = False` and clear proxy env vars
- **PowerShell**: Use `Invoke-WebRequest` without proxy (it usually bypasses for localhost)

```python
import os, requests
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
session = requests.Session()
session.trust_env = False  # bypass system proxy
resp = session.get("http://localhost:3100/status")
```

---

## Periodic Scheduler Integration

### Configuration (schedule.yaml)

Add `whatsapp` to any task's `notify` section:

```yaml
tasks:
  - name: check-waiting-for-me
    script: scripts/check_waiting_for_me.py
    schedule: delta 6h
    working_dir: C:\Projects\Swarmer
    enabled: true
    notify:
      on_failure: true
      on_success: false          # set true to get success notifications too
      email: user@example.com
      whatsapp: "+972547885798"  # ← WhatsApp notification
```

### How It Works

When a task completes, the scheduler checks the `notify` policy:
- **`on_failure: true`** + task failed → sends WhatsApp failure alert
- **`on_success: true`** + task succeeded → sends WhatsApp success summary

The message includes task name, status, duration, error details.

### Example Failure Notification

```
⚠️ *Periodic Task Failure*

❌ *check-waiting-for-me*
   Status: failed
   Exit code: 1
   Attempts: 3
   Duration: 45.2s
   Error: Script returned non-zero exit code

— _Periodic Scheduler_
```

### Programmatic Use

```python
from periodic.whatsapp import send_whatsapp_notification
from periodic.models import RunResult, TaskStatus

results = [RunResult(task_name="my-task", status=TaskStatus.FAILED, return_code=1)]
send_whatsapp_notification("+972547885798", results, on_failure=True)
```

---

## Bot Development

### Auto-Reply (in server.js)

Add to the `client.on('message')` handler in `server.js`:

```javascript
client.on('message', async msg => {
    // Keyword-based auto-reply
    if (msg.body.toLowerCase() === 'status') {
        msg.reply('✅ All systems operational.');
    }

    // Forward to AI
    if (msg.body.startsWith('!ask ')) {
        const question = msg.body.slice(5);
        // Call your AI API, get answer
        msg.reply(`🤖 Processing: "${question}"...`);
    }
});
```

### Polling Bot (Python)

```python
import time
from periodic.whatsapp import WhatsAppClient

wa = WhatsAppClient()
seen = set()

while True:
    for msg in wa.get_messages(limit=10):
        msg_id = f"{msg['from']}_{msg['timestamp']}"
        if msg_id not in seen:
            seen.add(msg_id)
            if "help" in msg["body"].lower():
                phone = msg["from"].replace("@c.us", "")
                wa.send(phone, "How can I help you?")
    time.sleep(5)
```

### Unanswered Message Checker

```python
from periodic.whatsapp import WhatsAppClient

wa = WhatsAppClient()
chats = wa.get_chats(limit=50)

unanswered = [
    c for c in chats
    if c.get("lastMessage")
    and not c["lastMessage"].get("fromMe")
    and not c["isGroup"]
]

for c in unanswered:
    print(f"  {c['name']}: {c['lastMessage']['body'][:60]}")
```

---

## Session Management

### Session Persistence

The WhatsApp session is stored in `.wwebjs_auth/` inside the server directory. This folder contains the browser session data that authenticates with WhatsApp servers.

**Session survives:**
- Server restarts
- Computer reboots
- Network disconnects

**Session expires when:**
- You delete the `.wwebjs_auth/` folder
- You log out via WhatsApp → Settings → Linked Devices → remove the device
- WhatsApp forces re-authentication (~weeks to months, rare)

### Re-Authentication

If the session expires:
1. Delete `.wwebjs_auth/` folder (if corrupted)
2. Restart `node server.js`
3. Scan the new QR code

### Backup

To preserve the session, back up the `.wwebjs_auth/` folder.

---

## Troubleshooting

### Server won't start: `EADDRINUSE`

Another instance is already running on port 3100.

```powershell
Stop-Process -Name "node" -Force
Start-Sleep 2
node server.js
```

Or change the port: `$env:WA_PORT = "3200"; node server.js`

### QR code not appearing

The client is likely already authenticated. Check the terminal for `✓ Authenticated`.

### Python can't connect (timeout)

1. Verify the server is running: `curl http://localhost:3100/status`
2. Check if a proxy is interfering — the request is to `localhost`, which should bypass proxies.
3. Increase timeout in the Python client.

### Messages not sending

- Verify `wa.is_ready()` returns `True`
- Phone number must include country code without `+` prefix in the chat ID (handled automatically)
- The recipient must have WhatsApp installed

### Server hangs at "Initializing WhatsApp client..."

Puppeteer Chrome is missing or session is stale:
1. Run `npx puppeteer browsers install chrome` in the server directory
2. If still stuck, delete `.wwebjs_auth/` and re-scan QR (see "Session Stale After Chrome Update" above)

### 403 from localhost requests (corporate proxy)

The corporate proxy intercepts even localhost requests. In Python, use `session.trust_env = False`. See "Corporate Proxy blocks localhost" section above.

### `getChatById` fails with `waitForChatLoading`

The chat uses `@lid` format. Use `/chat-by-name` endpoint instead of `/chat-history/:phone`. See "@lid vs @c.us Chat IDs" section above.

### Session expired

Terminal shows QR code again on startup. Scan it with your phone.

### `pywhatkit` vs `whatsapp-web.js`

| Feature | pywhatkit (Python) | whatsapp-web.js (Node.js) |
|---------|-------------------|--------------------------|
| Send messages | ✅ (opens browser tab) | ✅ (headless) |
| Receive messages | ❌ | ✅ |
| Auto-reply | ❌ | ✅ |
| Send media | Limited | ✅ |
| Background service | ❌ | ✅ |
| Session persistence | ❌ | ✅ |

**Recommendation**: Use the Node.js REST API approach for all production use.

---

## Dependencies

### Node.js (server)
- `whatsapp-web.js` — WhatsApp Web client
- `express` — HTTP server
- `qrcode-terminal` — Terminal QR code display
- `qrcode` — QR code image generation

### Python (client)
- `requests` — HTTP client (already in Swarmer env)
- `pywhatkit` — Alternative simple sender (in `requirements.txt`)
