---
name: managed-project-setup
description: "Scaffold a new managed project with spec, backlog, traceability, and manager process. Creates the full docs/ structure (spec.md, backlog.md, manager.md) with numbered requirements, EPICs, sprints, features, and cross-references. Includes interview phase to gather project goals. TRIGGER: user says 'new managed project', 'setup managed project', 'create spec and backlog', 'init project with tracking', 'scaffold project with spec', 'create a project like ClaudeLauncher', or 'managed project'."
---

<MANDATORY>
When this skill is used, begin your response with:
"[Using Skill: managed-project-setup]" followed by a brief statement of what you're doing.
This is non-negotiable. Do it BEFORE any other output.
</MANDATORY>

# Managed Project Setup

Scaffold a fully-tracked project workspace with spec, backlog, traceability matrix, and manager process file. This is the user's standard approach for non-trivial tools.

## Overview

A managed project has four core docs that work together:

| File | Purpose |
|------|---------|
| `docs/spec.md` | Requirements (REQ-xx), design, constraints, acceptance |
| `docs/backlog.md` | EPICs, Sprints, Features (F-xxx), traceability matrix, status |
| `docs/manager.md` | The process: sprint workflow, rules, definitions of done |
| `docs/dashboard.html` | Live progress visualization (updated every sprint) |

The traceability chain: **REQ → Feature → Test → Code**. No orphans at any level.

## Phase 1: Interview

Before creating anything, interview the user to gather:

1. **What is this tool?** (one-sentence elevator pitch)
2. **Who is it for?** (target users)
3. **Core capabilities** (3-7 bullet points of what it must do)
4. **Technology constraints** (language, framework, platform, packaging)
5. **Distribution model** (exe, web app, script, npm package, etc.)
6. **Security/secret management needs** (keys, tokens, auth)
7. **UX philosophy** (minimal? feature-rich? CLI? GUI?)

Use `vscode_askQuestions` for structured input, or accept freeform text.

After gathering answers, proceed to Phase 2.

## Phase 2: Generate Spec

Create `docs/spec.md` following this structure:

```markdown
# <Project Name> — Product Specification

**Version:** 1.0 Draft
**Date:** <today>
**Status:** Under Review

---

## 1. Overview
<elevator pitch + design principle>

## 2. <Category 1> (e.g., Distribution & Packaging)
| Requirement | Detail |
...

## 3. <Category 2> (e.g., Secret Management)
...

## N. Out of Scope (v1)
- items explicitly deferred

## N+1. UX Principles
1. ...
```

### Spec Rules

- Every table row or bullet that states a "shall" or "must" is a requirement.
- Requirements will be numbered REQ-01, REQ-02, ... in the backlog (not in the spec itself to keep it readable).
- Include wireframe layouts as ASCII art where applicable.
- End with a UX Principles section (3-5 rules for consistent decision-making).

## Phase 3: UX Review

After generating the spec, switch to UX expert mode:

1. Review the spec for UX anti-patterns:
   - Too many menus for a simple tool?
   - Redundant UI elements?
   - Multi-step flows that should be combined?
   - Power-user features blocking the happy path?
2. Present 5-10 specific UX improvement suggestions with rationale.
3. Ask the user which to apply.
4. Update the spec.

## Phase 4: Generate Backlog

Create `docs/backlog.md` following this structure:

```markdown
# <Project Name> — Implementation Backlog

**Created:** <today>
**Tracks:** [docs/spec.md](spec.md) rev 1

---

## Spec Requirements Index

| ID | Spec Section | Requirement |
|----|-------------|-------------|
| REQ-01 | §2 | ... |
...

## EPIC 1: <Name>
*<one-line description>*

### Sprint 1 — <Title>

| ID | Feature | Reqs | Description |
|----|---------|------|-------------|
| F-001 | ... | REQ-xx, REQ-yy | ... |
...

## Sprint Plan Summary
| Sprint | EPIC | Focus | Features |
...

## Traceability Matrix
| REQ | Feature(s) |
...

## Status Tracking
| Feature | Status | Sprint | Notes |
...
```

### Backlog Rules

- Every requirement from the spec gets a REQ-xx ID.
- Every REQ maps to at least one Feature (F-xxx).
- Every Feature maps back to its REQs.
- Sprints are ordered by dependency (foundation first, polish last).
- The traceability matrix is the contract: 100% coverage required.
- Status tracking table lists every feature with Not Started / In Progress / Completed.

## Phase 5: Generate Manager

Create `docs/manager.md` with the sprint workflow process. Use ClaudeLauncher's manager as the template:

### Required Sections

1. **Cardinal Rules** — git push rules, env usage, tracking integrity, no ad-hoc edits
2. **Files This Process Touches** — table of docs + their roles
3. **The Sprint Workflow** — 8 steps:
   - Step 1: Context Load
   - Step 2: Sprint Planning
   - Step 3: Write Tests First
   - Step 4: Implement
   - Step 5: Full Regression
   - Step 6: Sprint Review & Demo
   - Step 7: Post-Mortem
   - Step 8: Advance
4. **Mid-Sprint Changes** — Path A (fix now) vs Path B (defer), formal process for both
5. **Tracking Integrity Checks** — table of invariants to verify each sprint
6. **Quick Command Map** — what the user says → what Copilot does
7. **Definition of Done** — Sprint level and Epic level checklists
8. **Environment & Technical Rules** — venv, package management, test runner, build, etc.
9. **Project Structure (Target)** — ASCII tree of expected final layout

### Manager Customization

Adapt these sections to the project's technology:
- If it's a web app: add deploy procedures, rollback, staging
- If it's a GUI: add build/package step, demo instructions
- If it's a library: add publish step, API docs generation
- If it's hardware-related: add simulation, synthesis steps

## Phase 6: Generate Dashboard

Create `docs/dashboard.html` — a self-contained HTML file showing live project progress.

### Dashboard Contents

- **Overall progress bar** — features completed / total (percentage)
- **Epic breakdown** — per-epic progress (bar chart or table)
- **Current sprint** — which sprint is active, features in progress
- **Status counts** — Not Started / In Progress / Completed
- **Upcoming** — next sprint preview
- **Last updated** timestamp

### Dashboard Rules

- Single HTML file, no external dependencies (inline CSS/JS).
- Data is hardcoded in a `<script>` block as JSON — updated each sprint by Copilot.
- Opens directly in a browser (no server needed).
- Styled to match project theme (dark/light).
- Updated at the end of every sprint (Step 8 in the workflow).

### Template Structure

```html
<!DOCTYPE html>
<html>
<head><title>Project Dashboard</title></head>
<body>
  <h1>Project Name — Progress Dashboard</h1>
  <div id="progress"></div>
  <div id="epics"></div>
  <div id="current-sprint"></div>
  <script>
    const data = { /* updated each sprint */ };
    // render logic
  </script>
</body>
</html>
```

## Phase 7: Verify Integrity

After all four docs are created, run the traceability check:

1. Count REQs in spec vs REQs in backlog → must match.
2. Every REQ has at least one Feature → no orphans.
3. Every Feature traces to at least one REQ → no untraced work.
4. Sprint dependency order makes sense (no sprint depends on a later sprint).
5. Report: "X requirements, Y features, Z sprints. Full coverage verified."

## Phase 8: Handoff

Present summary to the user:
- Total requirements / features / sprints
- Estimated sprint flow (what comes first, what's last)
- Any open questions or decisions deferred
- Dashboard created and ready to track
- Ask: "Spec, backlog, and dashboard ready. Want me to start Sprint 1?"

---

## Reference Implementation

The canonical example of this process in action:
- `C:\Projects\ClaudeLauncher\docs\spec.md`
- `C:\Projects\ClaudeLauncher\docs\backlog.md`
- `C:\Projects\ClaudeLauncher\docs\manager.md`
- `C:\Projects\ClaudeLauncher\docs\dashboard.html`

Use these as structural templates. Adapt content to the new project's domain.

---

## Anti-Patterns to Avoid

- **Don't over-spec.** If the project is simple (5-10 features), don't create 13 sprints. Scale the process to the project size.
- **Don't spec implementation details.** Spec says WHAT, not HOW. Implementation lives in code.
- **Don't create empty sprints.** Every sprint must deliver user-visible value.
- **Don't front-load all polish.** Foundation → working features → polish. Never polish before it works.
- **Don't skip the UX review.** Even CLI tools benefit from UX thinking (error messages, flag naming, help text).
