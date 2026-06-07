---
name: Automation Dedup Guard
description: >
  Prevent duplicate sends and posts in automation workflows.
---

# Automation Dedup Guard

## Copilot Automation: Preventing Duplicate Sends & Posts

**Source**: Drory Shohat (email, 2026-02-11)
**For**: Anyone building AI-driven automation (Copilot, LLM agents) that sends emails or posts

---

## The Bug

When GitHub Copilot runs PowerShell commands in VS Code, the terminal output sometimes gets **truncated** (cut off). Copilot interpreted this as a failure and **retried the command** — but the first attempt had already succeeded.

**Result**: Duplicate posts on Viva Engage and duplicate emails in Outlook.

---

## Root Cause

**Terminal output truncation ≠ command failure.**

Both `Outlook .Send()` and Yammer `Invoke-RestMethod` execute fully even when the terminal output appears cut off.

---

## The Fix

| # | Fix | Details |
|---|-----|---------|
| 1 | **Send-guard variables** | Set `$emailSent = $true` after sending; check before any retry |
| 2 | **Verify-before-retry** | Check Sent Items folder or read latest Yammer messages before re-executing |
| 3 | **Dedup in sync script** | `Sync-CtrlAltVent.ps1` checks if a similar message was posted in the last 5 minutes |
| 4 | **Updated Copilot instructions** | Explicit rules in `.github/copilot-instructions.md` to NEVER retry on truncated output |

---

## Rule of Thumb

> If the command ran without a PowerShell error (no red text, no catch block triggered), it **succeeded** — regardless of what the terminal output looks like.

---

## Lessons for AI Automation

These principles apply to **any** AI-driven automation, not just Copilot:

1. **Treat API calls as non-idempotent by default** — sending = side effect
2. **Always verify state before retrying** — read before write
3. **Truncated output ≠ failure** — check the actual result
4. **Use guard variables** — track whether an action has already been performed
5. **Add dedup guards in scripts** — check for recent duplicates before executing

---

## Example: Send-Guard Pattern (PowerShell)

```powershell
$emailSent = $false

if (-not $emailSent) {
    $mail = $outlook.CreateItem(0)
    $mail.To = "recipient@example.com"
    $mail.Subject = "Subject"
    $mail.Body = "Content"
    $mail.Send()
    $emailSent = $true
    Write-Host "Email sent successfully"
}
```

## Example: Verify-Before-Retry Pattern

```powershell
# Before retrying a Viva Engage post, check if it already exists
$recentPosts = Get-VivaEngagePosts -Last 5
$alreadyPosted = $recentPosts | Where-Object { $_.Body -like "*your unique content*" }

if (-not $alreadyPosted) {
    # Safe to post
    Invoke-RestMethod -Uri $postUrl -Method POST -Body $body
}
```

---

**Created**: February 11, 2026
**Author**: Drory Shohat
