---
name: agentic-github-flow
description: >
  Set up and operate the agentic GitHub flow pattern: GitHub Issues as tasks, GitHub Actions as the agent brain, CI as the impartial judge, labels as a state machine. Covers repo scaffolding, workflow YAML authoring, self-hosted runner setup, Azure OpenAI wiring, troubleshooting, and BKMs from a working end-to-end run on Windows. Use when the user wants to set up an autonomous agent on any GitHub repo, extend the pattern to new repos, debug a workflow, add new phases, or understand how the system works.
  TRIGGER: user says "agentic github", "agent loop", "github actions agent", "llm github flow", "autonomous github", "set up the agent pattern", "new repo same methodology", "copy the agent setup", "github state machine", "label state machine".
---

# Agentic GitHub Flow — BKM & Methodology

## What this pattern is

GitHub as a state machine for autonomous agent work:

| Role | Component |
|---|---|
| Units of work | GitHub Issues (with Goal + Success Criteria) |
| Agent brain | GitHub Actions workflows |
| Impartial judge | CI (pytest — the agent cannot self-certify) |
| State machine | Issue labels |
| Audit trail | Issue comments (every LLM call logged) |

## State machine

```
agent:queued  →  (deps met, orchestrator fires)  →  agent:ready
agent:ready   →  [Phase 1: plan]  →  agent:in-progress
                                          ↓
                                   [Phase 2: code+PR]
                                          ↓
                                   [Phase 3: CI/pytest — dispatched by Phase 2]
                                          ↓
                               agent:done  OR  agent:blocked
```

`agent:queued` = created but dependencies not yet met (future orchestrator manages this).
Multiple issues can be `agent:in-progress` simultaneously — parallelism is free.

---

## Step 0 — MISSION.md (always fill this first)

**`MISSION.md`** in the repo root is the single source of truth for what the project is building.
The future `agent-plan-mission.yml` will read it and decompose it into GitHub Issues automatically.
Until that exists, create issues manually from the Areas of Work section.

### MISSION.md format

```markdown
# Mission
> One sentence. What are we building and why?

## Context
Why does this exist? 2–5 sentences of background.

## Goals
- [ ] Goal 1
- [ ] Goal 2

## Tech Stack
| Concern | Decision |
|---|---|
| Language | Python 3.11 |
| Test framework | pytest |

## Areas of Work
Ordered, dependency-aware. Mark parallel-safe ones with [parallel].
1. Area A
2. Area B  [parallel with A]
3. Area C  (depends on A)

## Out of Scope
- Item 1

## Human-in-the-Loop Checkpoints
- [ ] After initial plan is posted (before code)
- [ ] After each PR is opened (before merge)

## Constraints
| Constraint | Value |
|---|---|
| Max LLM calls/day | 50 |
| Max open PRs | 3 |
| Merge policy | Manual (human merges) |
```

### Issue body convention (for dependency ordering)

Add a `Depends on:` section to any issue that has prerequisites:
```markdown
## Depends on
- #3
- #7
```
The orchestrator checks this before promoting `agent:queued` → `agent:ready`.

---

## Infrastructure requirements

### Azure OpenAI
- Deployment name: `gpt-5.4` (or whatever is available)
- API version: `2024-12-01-preview`
- **Use `max_completion_tokens`, NOT `max_tokens`** — newer models reject the old param
- Store as repo secrets: `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`

### Self-hosted runner (Windows)
Needed when the GitHub org has IP allowlisting that blocks cloud runners.

1. Go to repo → Settings → Actions → Runners → New self-hosted runner
2. Download and run the setup on the Windows machine
3. Register with labels `self-hosted, windows`
4. **One-time auto-start setup** — run this in an **elevated (Admin)** PowerShell once:
   ```powershell
   $action = New-ScheduledTaskAction -Execute "powershell.exe" `
     -Argument '-WindowStyle Minimized -NonInteractive -Command "Set-Location C:\actions-runner; .\run.cmd"'
   $trigger = New-ScheduledTaskTrigger -AtLogOn
   $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) `
     -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 2) -StartWhenAvailable $true
   Register-ScheduledTask -TaskName "GitHubActionsRunner" -Action $action `
     -Trigger $trigger -Settings $settings -RunLevel Highest -Force
   Start-ScheduledTask -TaskName "GitHubActionsRunner"
   ```
   After this, the runner starts automatically on every login — no manual action needed.
5. Manual start (if needed): `Start-Process -FilePath "C:\actions-runner\run.cmd" -WorkingDirectory "C:\actions-runner" -WindowStyle Minimized`
6. Note: `svc.cmd` (Windows Service install) is NOT present in this runner build — use Task Scheduler instead.
7. Add to runner `.env` to ensure Git is on PATH: `PATH=C:\Program Files\Git\bin;...rest...`

**How it works when your PC is off:** The orchestrator (GitHub cloud cron) keeps running and checks deps. When an issue becomes ready it applies `agent:ready`. The job queues on GitHub (up to 30 days). When your runner comes back online it picks up queued jobs automatically.

### gh CLI
- Install from https://cli.github.com/
- Auth: `gh auth login` → select GitHub.com → HTTPS → token
- SSO: `gh auth refresh -h github.com -s repo,read:org` then authorize at the org portal
- Set proxy before any `gh` call: `$env:HTTPS_PROXY = "http://proxy.example.com:8080"`

---

## Workflow files

All three files go in `.github/workflows/`.

### Phase 1 — `agent-pick-issue.yml`

Triggers on `agent:ready` label. Calls LLM, posts plan as comment, flips label to `agent:in-progress`, then dispatches Phase 2 via `workflow_dispatch`.

Key requirements:
- `permissions: issues: write, contents: read, actions: write`
- `actions: write` is needed so `gh workflow run` can dispatch Phase 2
- Use `shell: powershell` (NOT `shell: bash` — WSL bash can't open Windows runner temp files; NOT `shell: pwsh` — PS7 not installed by default)
- Build the JSON payload as a PS hashtable → `ConvertTo-Json -Depth 10` → write to `$env:RUNNER_TEMP\payload.json`
- Call LLM with `Invoke-RestMethod -Body ([System.IO.File]::ReadAllText(...))` — **NOT** `-InFile` (causes 400 errors)
- Proxy: `Invoke-RestMethod` does NOT honor `HTTP_PROXY` env vars — use `-Proxy "http://..."` if needed, or set no-proxy for internal endpoints
- Write output to `$env:GITHUB_OUTPUT` using the heredoc pattern: `"KEY<<EOF" | Out-File -Append; $value | Out-File -Append; "EOF" | Out-File -Append`
- Pass LLM output to `actions/github-script` via `env:` block → `process.env.KEY` (NOT template literals with `${{ steps.x.outputs.KEY }}` — breaks when output contains backticks)
- Dispatch Phase 2: `gh workflow run agent-write-code.yml --repo $env:REPO -f issue_number=$env:ISSUE_NUMBER`

### Phase 2 — `agent-write-code.yml`

Triggered by `workflow_dispatch` (from Phase 1) with input `issue_number`.

Key requirements:
- Add both trigger types:
  ```yaml
  on:
    issues:
      types: [labeled]           # catches manual agent:in-progress label
    workflow_dispatch:
      inputs:
        issue_number:
          required: true
          type: string
  ```
- Fetch issue details via `actions/github-script` at the start (can't rely on `github.event.issue.*` when triggered via dispatch)
- LLM system prompt: instruct it to return ONLY a `\`\`\`json` block containing an array of `{path, content}` objects
- Extract with PS regex: `if ($raw -match '(?s)\`\`\`json\s*(.*?)\s*\`\`\`')`
- Write files with `[System.IO.File]::WriteAllText($f.path, $f.content)`
- Commit as `github-actions[bot]` and push to the new branch
- Open PR body must contain `Closes #N` — CI uses this to find the linked issue
- **Final step: dispatch CI** — Phase 2 must explicitly fire CI because GITHUB_TOKEN pushes cannot trigger `pull_request` events (GitHub security restriction):
  ```powershell
  gh workflow run ci.yml --repo $env:REPO -f pr_number=$env:PR_NUMBER
  ```
  Requires `actions: write` permission and `GH_TOKEN: ${{ github.token }}` in the step env.

### Phase 3 — `ci.yml`

Triggers via `workflow_dispatch` (dispatched by Phase 2) with input `pr_number`. Also triggers on `pull_request` for human-pushed PRs.

Key requirements:
- `runs-on: [self-hosted, windows]`
- Do NOT use `actions/setup-python` — it tries to download Python from the internet (slow/blocked on corp network). Use the system Python path directly:
  ```powershell
  $python = "C:\Users\<you>\AppData\Local\Programs\Python\Python311\python.exe"
  & $python -m pip install pytest --quiet
  & $python -m pytest --tb=short 2>&1 | Tee-Object -FilePath "$env:RUNNER_TEMP\pytest_output.txt"
  ```
- Use `continue-on-error: true` on the pytest step so post-steps still run
- First step must resolve the PR via API (works for both `pull_request` and `workflow_dispatch` triggers):
  ```javascript
  const num = context.payload.pull_request?.number ?? parseInt('${{ inputs.pr_number || 0 }}');
  const pr = await github.rest.pulls.get({ owner, repo, pull_number: num });
  // then checkout pr.data.head.sha explicitly
  ```
- Find linked issue from PR body: `body.match(/Closes #(\d+)/i)`
- Pass PR url to JS steps via `env:` block, not template literals
- On success: remove `agent:in-progress`, add `agent:done`, post comment
- On failure: remove `agent:in-progress`, add `agent:blocked`, post pytest output as comment

---

## Known gotchas

| Symptom | Root cause | Fix |
|---|---|---|
| `400 Bad Request` from Azure OpenAI | `-InFile` sends wrong content-type | Use `-Body ([System.IO.File]::ReadAllText(...))` |
| `max_tokens` param error | New models use `max_completion_tokens` | Rename the param |
| `pwsh: command not found` | PS7 not installed on runner | Use `shell: powershell` (PS5) |
| `bash: cannot open temp file` | WSL bash, not Git bash, resolves as `/bin/bash` | Use `shell: powershell` |
| Phase 2 never fires after Phase 1 | GITHUB_TOKEN can't trigger new workflow runs | Phase 1 must explicitly `gh workflow run` Phase 2 |
| `403: Resource not accessible` on dispatch | Missing `actions: write` permission | Add to `permissions:` block in Phase 1 |
| CI never fires on PR | setup-python hangs downloading Python | Remove `actions/setup-python`, use system Python path |
| CI fires but issue label doesn't flip | Agent wrote `${{ steps.x.outputs.y }}` in JS string | Pass via `env:` block, read with `process.env.KEY` |
| CI never fires automatically after Phase 2 PR | GITHUB_TOKEN push cannot trigger `pull_request` events | Phase 2 must `gh workflow run ci.yml -f pr_number=N` explicitly |
| CI reads wrong PR data when dispatch-triggered | `context.payload.pull_request` is null on dispatch | Resolve PR via API using `inputs.pr_number`, checkout `head.sha` explicitly |

---

## Checklist: new repo setup

- [ ] Fill in `MISSION.md` before anything else
- [ ] Create repo with issue template (Goal / Success Criteria / Acceptance Tests)
- [ ] Create labels: `agent:queued`, `agent:ready`, `agent:in-progress`, `agent:done`, `agent:blocked`
- [ ] Add secrets: `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`
- [ ] Register self-hosted Windows runner with labels `self-hosted, windows`
- [ ] Set up runner auto-start via Task Scheduler (elevated PowerShell, one-time)
- [ ] Copy `agent-pick-issue.yml`, `agent-write-code.yml`, `ci.yml` from reference repo
- [ ] Update Python path in `ci.yml` to match local machine
- [ ] Verify runner is online (Settings → Actions → Runners)
- [ ] Create a test issue, add `agent:ready`, watch Actions tab
- [ ] Confirm full loop: plan comment → branch → PR → CI → `agent:done`

---

## Re-trigger pattern (for debugging)

```powershell
# Set env for this terminal session
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
$env:HTTPS_PROXY = "http://proxy.example.com:8080"
$env:HTTP_PROXY  = "http://proxy.example.com:8080"

# Cycle labels to re-fire Phase 1
gh issue edit $ISSUE --repo $REPO --remove-label "agent:ready"
Start-Sleep -Seconds 2
gh issue edit $ISSUE --repo $REPO --add-label "agent:ready"

# Check runs
gh run list --repo $REPO --limit 5 --json databaseId,name,conclusion,status,headBranch | ConvertFrom-Json | Format-Table

# Tail failure log
gh run view $RUN_ID --repo $REPO --log-failed | Select-Object -Last 20

# Cancel a stuck run
gh run cancel $RUN_ID --repo $REPO
```

---

## Orchestrator design (future — not yet built)

File: `agent-orchestrate.yml`
Trigger: `schedule: '*/5 * * * *'` (every 5 min, GitHub cloud, always on)

Logic:
1. Fetch all issues labeled `agent:queued`
2. For each, parse `Depends on: #N` from the issue body
3. Check if all referenced issues have label `agent:done`
4. If yes → remove `agent:queued`, add `agent:ready` → Phase 1 fires
5. If no → leave queued

Parallelism is automatic — multiple issues can be `agent:in-progress` at once.
The runner queues jobs; add more self-hosted runners for true parallel execution.

---

## Reference repo

Working implementation: `https://github.com/example-org/issue_gen_experiment`
- `MISSION.md` — project mission template
- `CONTEXT.md` — technical log (runner name, secrets, current state)
- `flow.html` — living mission dashboard (open in browser for human-readable status)
- Completed Issue #1 end-to-end (hello.py, passing pytest, label → `agent:done`)
- Workflow files: `.github/workflows/agent-pick-issue.yml`, `agent-write-code.yml`, `ci.yml`
