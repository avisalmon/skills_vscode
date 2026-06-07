---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy. TRIGGER: user says "create a skill", "make a skill", "turn this into a skill", "improve this skill", "this skill isn't triggering", "optimize the skill description", or "test my skill".
---

# Skill Creator

A skill for creating new skills and iteratively improving them.

> **Adapted from Anthropic's skill-creator for VS Code Copilot.** The skill-writing
> philosophy below is Anthropic's and is model-agnostic. The *mechanics* (skill
> location, frontmatter format, how test runs and the description optimizer execute)
> have been reframed for this environment — VS Code Copilot on Windows, where skills
> live as folders under `~/.copilot/skills/` and there is no `claude` CLI. Where a
> step originally required Claude Code only, this file gives a VS Code equivalent.

At a high level, the process of creating a skill goes like this:

- Decide what you want the skill to do and roughly how it should do it
- Write a draft of the skill
- Create a few test prompts and run the-agent-with-access-to-the-skill on them
- Help the user evaluate the results both qualitatively and quantitatively
- Rewrite the skill based on feedback (and any glaring flaws the benchmarks expose)
- Repeat until you're satisfied
- Expand the test set and try again at larger scale

Your job when using this skill is to figure out where the user is in this process and
jump in to help them progress. If they say "I want to make a skill for X", help narrow
it down, write a draft, write test cases, run them, and iterate. If they already have a
draft, jump straight to the eval/iterate part of the loop. And if the user says "I don't
need a bunch of evaluations, just vibe with me" — do that instead. Be flexible.

After the skill is in good shape, you can also run the **description optimizer** to
improve how reliably the skill triggers.

## Environment facts for this setup

These are the concrete, environment-specific facts that override the original
Anthropic instructions. Everything else in this file applies as written.

| Topic | This environment (VS Code Copilot / Windows) |
|-------|----------------------------------------------|
| Skill location | `%USERPROFILE%\.copilot\skills\<skill-name>\SKILL.md` |
| Skill format | A folder containing `SKILL.md` (+ optional `scripts/`, `references/`, `assets/`). **No `.skill` package, no install step** — the folder *is* the skill. |
| Frontmatter | YAML with `name` + `description` (see below). The skill is surfaced to the agent via the `<skill>` block in `copilot-instructions.md`. |
| Subagents | This agent has `runSubagent` (e.g. the `Explore` agent). Use it for parallel test runs **if available**. If not, run test cases inline, one at a time. |
| Running test cases | Spawn subagents via `runSubagent`, or run inline. There is **no `claude -p` CLI**. |
| Description optimizer | The automated `scripts/run_loop.py` needs the `claude` CLI and does **not** run here. Use the **manual optimization workflow** in this file instead. |
| Shell | PowerShell on Windows. Use `Copy-Item -Recurse`, `Remove-Item`, `$PID`, etc. — not `cp -r`, `nohup`, `kill $PID`, `/tmp/`, `open`. |
| Browser viewer | `eval-viewer/generate_review.py` works (Python + a browser). On a headless box, pass `--static <path>` to emit a standalone HTML file. |

## Communicating with the user

This skill is used by people across a wide range of familiarity with coding jargon. Pay
attention to context cues to understand how to phrase your communication. In the default
case: "evaluation" and "benchmark" are borderline-OK; for "JSON" and "assertion" you want
real cues that the user knows those terms before using them unexplained. It's fine to
briefly define a term if you're in doubt.

---

## Creating a skill

### Capture Intent

Start by understanding the user's intent. The current conversation might already contain a
workflow the user wants to capture (e.g., they say "turn this into a skill"). If so,
extract answers from the conversation history first — the tools used, the sequence of
steps, corrections the user made, input/output formats observed. Have the user fill the
gaps and confirm before proceeding.

1. What should this skill enable the agent to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases to verify the skill works? Skills with objectively
   verifiable outputs (file transforms, data extraction, code generation, fixed workflow
   steps) benefit from test cases. Skills with subjective outputs (writing style, art)
   often don't. Suggest the appropriate default, but let the user decide.

### Interview and Research

Proactively ask about edge cases, input/output formats, example files, success criteria,
and dependencies. Wait to write test prompts until this is ironed out.

Check for similar skills first: look under `%USERPROFILE%\.copilot\skills\` to avoid
duplicating an existing skill, and read related `SKILL.md` files to match local
conventions. If the skill wraps an API or tool, check its docs. If subagents are available
and research would help, research in parallel via `runSubagent`; otherwise inline.

### Write the SKILL.md

Based on the interview, fill in these components:

- **name**: Skill identifier (kebab-case, matches the folder name).
- **description**: When to trigger and what it does. This is the **primary triggering
  mechanism** — include both what the skill does AND specific contexts for when to use it.
  All "when to use" info goes here, not in the body. The agent tends to **undertrigger**
  skills, so make descriptions a little "pushy": list specific trigger words/phrases. For
  example, instead of "Build a dashboard to display internal data", write "Build a
  dashboard to display internal data. Use this whenever the user mentions dashboards, data
  visualization, internal metrics, or wants to display any kind of company data, even if
  they don't explicitly say 'dashboard'." End with a `TRIGGER:` line of literal phrases.
- **the rest of the skill :)**

#### Frontmatter format (this environment)

```yaml
---
name: skill-name
description: >
  What it does and when to trigger. Be slightly pushy — list specific trigger
  words so the skill fires reliably.
  TRIGGER: user says "keyword1", "keyword2", "phrase3".
---
```

The skill is then exposed to the agent through a `<skill>` entry in the relevant
`copilot-instructions.md`:

```xml
<skill>
<name>skill-name</name>
<description>Same description as the frontmatter, including the TRIGGER line.</description>
<file>%USERPROFILE%\.copilot\skills\skill-name\SKILL.md</file>
</skill>
```

### Skill Writing Guide

#### Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

#### Progressive Disclosure

Skills use a three-level loading system:
1. **Metadata** (name + description) — always in context (~100 words)
2. **SKILL.md body** — in context whenever the skill triggers (<500 lines ideal)
3. **Bundled resources** — as needed (unlimited; scripts can execute without loading)

These counts are approximate; go longer if needed.

**Key patterns:**
- Keep SKILL.md under 500 lines; if approaching the limit, add a layer of hierarchy with
  clear pointers to where the model should go next.
- Reference files clearly from SKILL.md with guidance on when to read them.
- For large reference files (>300 lines), include a table of contents.

**Domain organization** — when a skill supports multiple domains/frameworks, organize by
variant so the agent reads only the relevant reference file:
```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

#### Principle of Lack of Surprise

Skills must not contain malware, exploit code, or anything that could compromise system
security. A skill's contents should not surprise the user given its description. Don't
create misleading skills or skills designed to facilitate unauthorized access, data
exfiltration, or other malicious activity. (Things like "roleplay as an X" are fine.)

#### Writing Patterns

Prefer the imperative form in instructions.

**Defining output formats:**
```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**Examples pattern:**
```markdown
## Commit message format
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

#### Writing Style

Explain to the model **why** things are important rather than relying on heavy-handed
musty MUSTs. Use theory of mind; keep the skill general rather than narrow to specific
examples. Write a draft, then look at it with fresh eyes and improve it. (Exception:
genuinely safety-critical or destructive-action rules deserve strong, explicit language.)

### Register the skill

After writing `SKILL.md`, add the `<skill>` block (above) to the appropriate
`copilot-instructions.md` so the agent actually sees it in its skill list. A skill that
isn't registered will never trigger.

### Test Cases

After writing the draft, come up with 2-3 realistic test prompts — the kind of thing a
real user would actually say. Share them: "Here are a few test cases I'd like to try. Do
these look right, or do you want to add more?" Then run them.

Save test cases to `evals/evals.json`. Don't write assertions yet — just the prompts.
You'll draft assertions in the next step while runs are in progress.

```json
{
  "skill_name": "example-skill",
  "evals": [
    { "id": 1, "prompt": "User's task prompt", "expected_output": "Description of expected result", "files": [] }
  ]
}
```

See `references/schemas.md` for the full schema (including the `assertions` field).

## Running and evaluating test cases

This section is one continuous sequence — don't stop partway through.

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Within it,
organize by iteration (`iteration-1/`, `iteration-2/`, …) and within that, each test case
gets a directory (`eval-0/`, `eval-1/`, …). Create directories as you go, not upfront.

### Step 1: Spawn all runs (with-skill AND baseline) in the same turn

For each test case, you want two runs — one **with** the skill, one **baseline** (without).
If `runSubagent` is available, spawn both in the same turn so they finish around the same
time. If subagents are **not** available, run them inline one at a time (see "No-subagent
fallback" below).

**With-skill run** — give the subagent:
```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about — e.g., "the .docx file", "the final CSV">
```

**Baseline run** (same prompt; baseline depends on context):
- **Creating a new skill**: no skill at all. Save to `without_skill/outputs/`.
- **Improving an existing skill**: the old version. Before editing, snapshot the skill
  (`Copy-Item -Recurse <skill-path> <workspace>\skill-snapshot`), then point the baseline
  subagent at the snapshot. Save to `old_skill/outputs/`.

Write an `eval_metadata.json` per test case (assertions can be empty for now). Give each
eval a descriptive name based on what it tests — use that name for the directory too.

```json
{ "eval_id": 0, "eval_name": "descriptive-name-here", "prompt": "The user's task prompt", "assertions": [] }
```

**No-subagent fallback:** read the skill's `SKILL.md`, then follow its instructions to
accomplish the test prompt yourself, one at a time. This is less rigorous (you wrote the
skill and you're running it, so you have full context), but it's a useful sanity check and
the human review step compensates. You can skip the baseline runs in this mode — just use
the skill to complete each task.

### Step 2: While runs are in progress, draft assertions

Don't just wait. Draft quantitative assertions for each test case and explain them to the
user. Good assertions are objectively verifiable and have descriptive names that read
clearly in the viewer. Subjective skills (writing style, design quality) are better judged
qualitatively — don't force assertions onto things that need human judgment. Update
`eval_metadata.json` and `evals/evals.json` once assertions are drafted.

### Step 3: As runs complete, capture timing data

If subagent completions report `total_tokens` and `duration_ms`, save them immediately to
`timing.json` in the run directory:
```json
{ "total_tokens": 84852, "duration_ms": 23332, "total_duration_seconds": 23.3 }
```
Process each completion as it arrives. (If your environment doesn't surface token/timing
data, skip this — the qualitative review and assertion pass still work.)

### Step 4: Grade, aggregate, and launch the viewer

1. **Grade each run** — read `agents/grader.md` and evaluate each assertion against the
   outputs (spawn a grader subagent or grade inline). Save `grading.json` in each run
   directory. The `expectations` array must use the fields `text`, `passed`, and `evidence`
   — the viewer depends on these exact names. For assertions checkable programmatically,
   write and run a script rather than eyeballing it.

2. **Aggregate into a benchmark** — from the skill-creator directory:
   ```powershell
   python -m scripts.aggregate_benchmark <workspace>\iteration-N --skill-name <name>
   ```
   Produces `benchmark.json` + `benchmark.md` (pass_rate, time, tokens per config, mean ±
   stddev, delta). Put each `with_skill` config before its baseline counterpart. See
   `references/schemas.md` for the exact schema if generating manually.

3. **Analyst pass** — read the benchmark and surface patterns the aggregates hide (see
   `agents/analyzer.md`): non-discriminating assertions (always pass regardless of skill),
   high-variance/flaky evals, time/token tradeoffs.

4. **Launch the viewer** with both qualitative outputs and quantitative data:
   ```powershell
   python <skill-creator-path>\eval-viewer\generate_review.py `
     <workspace>\iteration-N `
     --skill-name "my-skill" `
     --benchmark <workspace>\iteration-N\benchmark.json
   ```
   For iteration 2+, also pass `--previous-workspace <workspace>\iteration-<N-1>`. On a
   headless machine, add `--static <output.html>` to write a standalone file instead of
   starting a server; the "Submit All Reviews" button then downloads `feedback.json`, which
   you copy into the workspace for the next iteration. Use `generate_review.py` — don't
   hand-write HTML.

5. **Tell the user**: "I've opened the results. The 'Outputs' tab lets you click through
   each test case and leave feedback; the 'Benchmark' tab shows the quantitative
   comparison. Come back here when you're done."

### Step 5: Read the feedback

When the user says they're done, read `feedback.json`:
```json
{ "reviews": [ { "run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..." } ], "status": "complete" }
```
Empty feedback means the user thought it was fine. Focus improvements on the cases with
specific complaints. If you started a viewer server, stop it when done (close the terminal
running it, or `Stop-Process -Id <pid>`).

---

## Improving the skill

This is the heart of the loop.

1. **Generalize from the feedback.** Skills are meant to be used many times across many
   prompts. You and the user iterate on a few examples because it's fast, but if the skill
   only works for those examples it's useless. Avoid fiddly overfit changes and oppressive
   MUSTs; if an issue is stubborn, try a different metaphor or working pattern.
2. **Keep the prompt lean.** Remove things that aren't pulling their weight. Read the
   transcripts, not just final outputs — if the skill makes the model waste time, cut the
   instruction causing it and see what happens.
3. **Explain the why.** Today's models have good theory of mind; given a good harness they
   go beyond rote instructions. If you're writing ALWAYS/NEVER in all caps or rigid
   structures, that's a yellow flag — reframe and explain the reasoning instead.
4. **Look for repeated work across test cases.** If every run independently wrote a similar
   helper script or took the same multi-step approach, that's a strong signal to bundle the
   script in `scripts/` and have the skill use it — saving every future invocation from
   reinventing the wheel.

Take your time thinking; thinking time is not the blocker. Write a draft revision, look at
it anew, and improve.

### The iteration loop

After improving the skill:
1. Apply your improvements.
2. Rerun all test cases into a new `iteration-<N+1>/` directory, including baselines. For a
   new skill the baseline stays `without_skill`; for an existing skill, use judgment (the
   original the user came in with, or the previous iteration).
3. Launch the viewer with `--previous-workspace` pointing at the previous iteration.
4. Wait for the user to review, then read the new feedback and repeat.

Keep going until the user is happy, the feedback is all empty, or you stop making
meaningful progress.

---

## Advanced: Blind comparison

For a more rigorous comparison between two versions (e.g., "is the new version actually
better?"), use the blind comparison system: read `agents/comparator.md` and
`agents/analyzer.md`. The idea is to give two outputs to an independent agent without
telling it which is which, let it judge quality, then analyze why the winner won. This is
optional and requires subagents; the human review loop is usually sufficient.

---

## Description Optimization (manual workflow for VS Code Copilot)

The description field is the primary mechanism that decides whether the agent invokes a
skill. After creating or improving a skill, offer to optimize the description for better
triggering accuracy.

> **Note:** The automated optimizer (`scripts/run_loop.py`, `run_eval.py`,
> `improve_description.py`) drives the `claude -p` CLI and Claude Code's
> `.claude/commands/` discovery, **neither of which exists in VS Code Copilot**. The
> scripts are kept in `scripts/` for reference / Claude Code users. In this environment,
> run the optimization **manually** as below.

### Step 1: Generate trigger eval queries

Create ~20 queries — a mix of should-trigger and should-not-trigger:
```json
[
  { "query": "the user prompt", "should_trigger": true },
  { "query": "another prompt", "should_trigger": false }
]
```
Make them realistic — concrete, specific, with detail (file paths, job context, column
names, company names, URLs, a little backstory). Some lowercase, abbreviated, or typo-y.
Mix lengths and focus on edge cases.

- **Bad:** `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`.
- **Good:** `"ok so my boss just sent me this xlsx (it's in my downloads, 'Q4 sales final FINAL v2.xlsx') and wants me to add a column showing profit margin as a %. revenue is col C, costs col D i think"`.

For **should-trigger** (8-10): different phrasings of the same intent, formal and casual,
cases where the user doesn't name the skill/file type but clearly needs it, uncommon use
cases, and cases where this skill competes with another but should win.

For **should-not-trigger** (8-10): the valuable ones are **near-misses** — queries that
share keywords/concepts but actually need something else. Avoid obviously-irrelevant
negatives ("write a fibonacci function" for a PDF skill tests nothing).

### Step 2: Review with the user

Present the eval set for review. You can use the HTML template at `assets/eval_review.html`:
1. Read the template.
2. Replace `__EVAL_DATA_PLACEHOLDER__` (the JSON array, no surrounding quotes),
   `__SKILL_NAME_PLACEHOLDER__`, and `__SKILL_DESCRIPTION_PLACEHOLDER__`.
3. Write to a temp file and open it (e.g. `Invoke-Item .\eval_review_<skill>.html`).
4. The user edits queries, toggles should-trigger, and clicks "Export Eval Set" (downloads
   to the Downloads folder). Or just review the queries inline in chat — that's fine too.

Bad eval queries lead to bad descriptions, so this review matters.

### Step 3: Optimize manually

Without the `claude -p` loop, iterate by hand:
1. For each query, judge honestly whether the **current** description would cause the agent
   to load the skill. Be strict — the agent only consults a skill it actually needs.
2. Find the misses: should-trigger queries that wouldn't fire (description too narrow /
   missing phrases) and should-not-trigger queries that would fire (description too broad /
   leaking into adjacent domains).
3. Propose a revised description that fixes those without breaking the passing cases. Add
   missing trigger phrases for under-triggering; tighten scope and add "do not use for…"
   guidance for over-triggering.
4. Re-judge all queries against the revision. Repeat until trigger accuracy is good and
   you're not overfitting to the train queries (hold a few back as a sanity check).
5. Show the user before/after and the reasoning, then apply the chosen description to both
   the `SKILL.md` frontmatter and the `<skill>` block in `copilot-instructions.md`.

### How skill triggering works

Skills appear in the agent's skill list with their name + description; the agent decides
whether to consult a skill based on that description. Importantly, the agent only consults
skills for tasks it can't easily handle on its own — simple one-step queries like "read
this PDF" may not trigger a skill even with a perfect description, because the agent can
just do them. So make your eval queries **substantive** — multi-step or specialized enough
that consulting a skill actually helps. Simple queries like "read file X" are poor tests.

---

## Packaging / install (this environment)

There is **no `.skill` package step** here. A skill is just its folder under
`%USERPROFILE%\.copilot\skills\<skill-name>\`. To "install" a skill, place the folder
there and register the `<skill>` block in `copilot-instructions.md`. (The Anthropic
`scripts/package_skill.py` exists for producing `.skill` bundles for Claude Code / Claude.ai
and is optional — not used by VS Code Copilot.)

**Updating an existing skill:** preserve the original directory name and `name` frontmatter
field. If the installed path is read-only, copy it to a writeable location, edit there, and
copy back.

---

## Reference files

`agents/` — instructions for specialized subagents; read when spawning the relevant one:
- `agents/grader.md` — evaluate assertions against outputs
- `agents/comparator.md` — blind A/B comparison between two outputs
- `agents/analyzer.md` — analyze why one version beat another

`references/`:
- `references/schemas.md` — JSON structures for evals.json, grading.json, benchmark.json, etc.

`scripts/` — helper scripts. `aggregate_benchmark.py`, `generate_report.py`, and
`quick_validate.py` are portable Python. `run_eval.py`, `run_loop.py`, and
`improve_description.py` require the `claude` CLI and are **Claude Code only** — use the
manual description-optimization workflow above instead.

---

Core loop, one more time for emphasis:
- Figure out what the skill is about
- Draft or edit the skill
- Run the-agent-with-access-to-the-skill on test prompts
- With the user, evaluate the outputs (build `benchmark.json`, run `generate_review.py`)
- Repeat until you and the user are satisfied
- Register the skill (and update its description for reliable triggering)

Add these steps to your todo list so you don't forget. Good luck!
