---
name: Vscode Tips
description: >
  VS Code tip: read markdown files beautifully.
---

# Vscode Tips

## bkm-vscode-md-preview

﻿# 🍬 VS Code Tip: Read Markdown Files Beautifully

## The Problem

Tired of seeing markdown files with all the `#`, `*`, `-`, and other markup symbols? Reading raw markdown can be exhausting.

## The Solution

Configure VS Code to automatically open `.md` files in **Preview mode** (rendered/styled) instead of raw markup.

## Setting to Add

```json
"workbench.editorAssociations": {
  "*.md": "vscode.markdown.preview.editor"
}
```

## How to Apply (Copilot Agent Instructions)

### For Copilot Agent - Do This:

1. **Run VS Code command** to open User Settings JSON:
   ```
   run_vscode_command: workbench.action.openSettingsJson
   ```

2. **Read the settings file** using this URI:
   ```
   settings.json
   ```

3. **Add the setting** at the top of the JSON object (after the opening `{`):
   ```json
   "workbench.editorAssociations": {
     "*.md": "vscode.markdown.preview.editor"
   },
   ```

4. **Done!** Takes effect immediately.

### Manual Method (User):

**Option 1: Settings UI**
1. Press `Ctrl+,` to open Settings
2. Search for "editor associations"
3. Click "Add Item"
4. Item: `*.md`
5. Value: `vscode.markdown.preview.editor`

**Option 2: Settings JSON**
1. Press `Ctrl+Shift+P`
2. Type: **Preferences: Open User Settings (JSON)**
3. Add the setting above

## Toggle Back to Raw Edit

If you need to edit the raw markdown:

- Right-click the tab → **Reopen Editor With...** → **Text Editor**
- Or use `Ctrl+K` then `V` to open preview side-by-side with editor

---

**Tip Credit**: הטיפ היומי 🎯
