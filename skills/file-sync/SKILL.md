---
name: file-sync
description: >
  Bidirectional and unidirectional file synchronization between local Windows
  and remote Linux workspaces. Uses MD5 hash-based comparison, deletion tracking,
  state persistence in JSON, and supports both Z: drive and SSH/SCP transport.
---

# File Sync — Local ↔ Remote Workspace Synchronization

## Overview

Synchronizes files between local Windows workspace and remote Linux servers.
Supports bidirectional (BKM docs) and unidirectional (RTL — remote is source of truth) modes.

## Key Files

| File | Purpose |
|------|---------|
| `Python/sync_BKM.py` | Bidirectional BKM sync via Z: drive |
| `Python/sync_BKM_ssh.py` | Bidirectional BKM sync via SSH/SCP |
| `Python/sync_RTL_ssh.py` | One-way RTL sync (remote → local) via SSH |

## Bidirectional Sync (BKM)

```python
class BKMSynchronizerSSH:
    def __init__(self, local_dir, remote_path, ssh_conn, dry_run=False, use_hash=True):
        self.local_dir = Path(local_dir)       # BKM/
        self.remote_path = remote_path          # /nfs/.../ww46/BKM/
        self.state_file = Path('.sync_state.json')
        self.sync_state = self.load_sync_state()
```

### Sync Algorithm

1. **Build file inventories**: List all `.md` files locally and remotely
2. **Hash comparison**: MD5 hash each file to detect changes
3. **Compare against last sync state** (stored in `.sync_state.json`):
   - File exists locally but not remotely → **Upload** (new local file)
   - File exists remotely but not locally → **Download** (new remote file)
   - Both exist, hashes differ:
     - Changed since last sync locally → **Upload** local version
     - Changed since last sync remotely → **Download** remote version
     - Both changed → **Conflict** (keep both, user resolves)
   - File was in last sync but now missing → **Deletion propagation**
4. **Update sync state** with new hashes

### State File Format (`.sync_state.json`)

```json
{
  "last_sync": "2025-11-15T10:30:00",
  "files": {
    "BKM/clock_gating_guide.md": {
      "hash": "a1b2c3d4...",
      "last_synced": "2025-11-15T10:30:00"
    }
  }
}
```

## One-Way RTL Sync

```python
# Remote is source of truth — always overwrite local
# Downloads all .sv/.svh files from remote RTL directory
python Python/sync_RTL_ssh.py --version ww46
```

After RTL sync, automatically runs `extract_rtl_structs.py` to regenerate Python parsers.

## Usage

```powershell
cd C:\Projects\Verilog\TokenOut
.\env\Scripts\Activate.ps1

# Preview BKM changes (dry run)
python Python/sync_BKM_ssh.py --dry-run

# Sync BKM docs + rebuild wiki
python Python/sync_BKM_ssh.py --build-wiki

# Sync RTL from remote
python Python/sync_RTL_ssh.py
```

## Safety Features

- **Dry-run mode**: Preview all changes without modifying files
- **Hash-based comparison**: Reliable detection (not just timestamps)
- **State persistence**: Tracks what was synced to detect deletions
- **Never auto-deletes without tracking**: Deletions are logged and propagated carefully
