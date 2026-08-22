# Project Engineering Notebook

Append new entries. Do not replace prior entries.

## 2026-08-20 — User → ChatGPT

Create a Codex counterpart to the existing Claude Usage Governor in the Codex Workflow projects directory and begin working on it.

## 2026-08-20 — ChatGPT → Codex

Create a production-oriented Codex plugin project named `codex-usage-governor`.

Product principles:

- Advisory only; never block Codex work.
- Prefer authoritative account usage and reset data.
- Keep observed, estimated, and projected values visibly distinct.
- Perform all arithmetic in deterministic code, never in model prose.
- Store only usage telemetry and configuration locally—never prompts, code, or conversation contents.
- Support Windows first without preventing macOS or Linux support.

First milestone:

1. Identify a supported machine-readable Codex usage source.
2. Capture representative payloads without secrets.
3. Define a provider-neutral usage-window schema.
4. Port and test sustainable-rate calculations against synthetic fixtures.
5. Integrate with Codex hooks and status-line capabilities only after the collector is proven.

## ChatGPT Review

Codex currently documents `/usage` views, `/status` rate limits, configurable rate-limit status-line fields, and lifecycle hooks. The unresolved question is whether account usage values are exposed to plugins or hooks in structured form. Terminal-screen scraping is not an acceptable production foundation unless explicitly selected as a temporary prototype.

## Questions for User

- Should the first release target ChatGPT subscription usage only, or also API-key billing?
- Should development optimize for the server's Codex CLI first, the desktop app first, or both equally?

## 2026-08-20 — Codex → ChatGPT

### Summary of completed work

Implemented the first functional Codex Usage Governor MVP. The collector reads structured rate-limit metadata from Codex session JSONL, normalizes it, and feeds a deterministic budgeting engine. Reports now cover current status, today, the governing reset window, local history, and configuration. Plugin hooks initialize storage and sample the current session after completed turns.

### Files created

- `plugin/codex-usage-governor/scripts/governor.py`
- `plugin/codex-usage-governor/hooks/hooks.json`
- `tests/test_governor.py`

### Files modified

- `README.md`
- `STATE.md`
- `TODO.md`
- `DECISIONS.md`
- `CHANGELOG.md`
- `plugin/codex-usage-governor/skills/usage-governor/SKILL.md`

### Architectural decisions

- Use structured `token_count.rate_limits` data, not rendered terminal text.
- Isolate session parsing behind a normalized data contract.
- Select the longest `codex` window as the current governing budget.
- Defer comparative model advice until its relationship to subscription metering is evidence-backed.

### Problems encountered

- Official validator scripts require `PyYAML`, which is absent from the installed Python 3.14 environment.
- Windows sandboxing prevents tests from using the default system temp directory; tests now use a project-local disposable directory.

### Verification

- Five unit tests pass.
- Python syntax compilation passes.
- Plugin and hook JSON parse successfully.
- Live collection on Codex CLI 0.147.0 produced a report from a Plus-plan seven-day usage window.
- A stored-row inspection confirmed no prompt or response fields.

### Next logical milestone

Install the plugin through a development marketplace, trust its hooks, complete several Codex turns, and verify automatic collection plus multi-session behavior.
