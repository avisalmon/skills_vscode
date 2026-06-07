---
name: M365 Graph MCP
description: >
  Microsoft 365 integration via the M365 Graph MCP server. EMAIL IS DISABLED.
  Do NOT use this skill for email operations (no send, no draft, no reply, no
  forward, no delete, no mark-read). For ALL email tasks, use the
  outlook-powershell skill instead (Outlook COM with $mail.Display()).
  This skill may still be used for Calendar read, Teams chats, OneNote,
  SharePoint, and OneDrive operations.
  DO NOT USE FOR: any email operation whatsoever, creating calendar events,
  modifying SharePoint site permissions, admin operations.
---

# M365 Graph MCP Server

## Overview
The M365 Graph MCP server gives Copilot **direct access to Microsoft 365** via the Microsoft Graph API. It runs as a local stdio MCP server and is configured globally in VS Code — available in every workspace.

## Configuration
- **Executable:** `%USERPROFILE%/.copilot/bin/m365-graph-mcp/m365-graph-mcp.exe`
- **Config file:** `%APPDATA%\Code\User\mcp.json`
- **Auth:** Interactive browser OAuth via MSAL (Microsoft Graph PowerShell client ID). Tokens are cached locally after first login.
- **Source repo:** `%USERPROFILE%\.copilot\example-m365-graph-agent\m365GraphAgentExample\`

## Available Tools (37 total)

### Email (12 tools)
| Tool | Purpose |
|------|---------|
| `email_search` | Search emails by query string |
| `email_get` | Get a specific email by ID |
| `email_send` | Send a new email |
| `email_reply` | Reply to an email |
| `email_forward` | Forward an email |
| `email_create_draft` | Create a draft email |
| `email_send_draft` | Send an existing draft |
| `email_flag` | Flag/unflag an email |
| `email_move` | Move email to a folder |
| `email_delete` | Delete an email |
| `email_mark_read` | Mark email as read/unread |
| `email_list_folders` | List mail folders |

### Calendar (4 tools)
| Tool | Purpose |
|------|---------|
| `calendar_get_events` | Get events for a date range |
| `calendar_get_event` | Get a specific event by ID |
| `calendar_list_calendars` | List all calendars |
| `calendar_search` | Search calendar events |

> **Note:** Calendar is **read-only**. To create meetings/events, use the `outlook-powershell` skill with Outlook COM: `$outlook.CreateItem(1)` (AppointmentItem).

### Teams (6 tools)
| Tool | Purpose |
|------|---------|
| `teams_list_chats` | List recent chats (max 50) |
| `teams_get_chat` | Get chat details + members |
| `teams_get_messages` | Get messages from a chat (max 50) |
| `teams_get_message` | Get a specific message |
| `teams_search_messages` | Search messages across all chats |
| `teams_send_message` | Send a message to a chat |

### OneNote (6 tools)
| Tool | Purpose |
|------|---------|
| `onenote_list_notebooks` | List all notebooks |
| `onenote_list_sections` | List sections in a notebook |
| `onenote_list_all_sections` | List all sections across notebooks |
| `onenote_list_pages` | List pages in a section |
| `onenote_get_page` | Get page content |
| `onenote_search_pages` | Search across all pages |

### SharePoint (7 tools)
| Tool | Purpose |
|------|---------|
| `sharepoint_list_sites` | List accessible SharePoint sites |
| `sharepoint_list_drives` | List document libraries on a site |
| `sharepoint_list_items` | List items in a drive/folder |
| `sharepoint_search` | Search across SharePoint |
| `sharepoint_upload_file` | Upload a file to SharePoint |
| `sharepoint_download_file` | Download a file from SharePoint |
| `sharepoint_delete_file` | Delete a file from SharePoint |

### OneDrive (2 tools)
| Tool | Purpose |
|------|---------|
| `onedrive_list_items` | List files/folders in OneDrive |
| `onedrive_search` | Search OneDrive files |

### User (2 tools)
| Tool | Purpose |
|------|---------|
| `user_get` | Get current user profile |
| `user_search` | Search for users by name/email |

## Common Workflows

### Email Triage
```
1. email_search query="is:unread" → get unread emails
2. Identify action items by sender and subject
3. email_mark_read on processed emails
```

### Find a Teams Conversation
```
1. teams_search_messages query="keyword" → search by content
2. If not found: teams_list_chats → browse chats
3. teams_get_chat chatId="..." → see members
4. teams_get_messages chatId="..." top=50 → get messages
```

### Download a Meeting Recording
```
1. teams_list_chats → find meeting chat
2. teams_get_messages → find message with recording link
3. sharepoint_download_file → download the MP4
```

### Create a Meeting (combo with outlook-powershell)
```
1. calendar_get_events → find free slots
2. user_search → get attendee email
3. Use Outlook COM: $outlook.CreateItem(1) → create appointment
   $appt.Subject = "..."; $appt.Start = "..."; $appt.Recipients.Add("email")
   $appt.Display()  # NEVER .Save() or .Send() without review
```

### Send Authenticated Email (combo with outlook-powershell)
```
# For rich emails that need review before sending, prefer Outlook COM:
$outlook = New-Object -ComObject Outlook.Application
$mail = $outlook.CreateItem(0)
$mail.To = "recipient@example.com"
$mail.Subject = "..."
$mail.HTMLBody = "..."
$mail.Display()  # User reviews and sends
```

## Known Limitations
- **Calendar:** Read-only (no create/update/delete events)
- **Teams messages:** Max 50 per request, no pagination cursor
- **Teams chats:** Max 50 per list call
- **SharePoint sites:** May return empty if tenant restricts Sites.Read.All
- **OneDrive:** Personal OneDrive works; shared drives depend on permissions
- **Auth:** First use requires interactive browser login; tokens cache after that
- **Email send:** Works but prefer Outlook COM + `.Display()` for review safety

## MANDATORY RULES
1. **NEVER auto-send emails** — always use `$mail.Display()` for user review
2. **NEVER delete emails/files** without explicit user confirmation
3. **NEVER send Teams messages** without user approval
4. For calendar event creation, use the `outlook-powershell` skill (COM), not Graph
