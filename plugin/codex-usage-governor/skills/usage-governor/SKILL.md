---
name: usage-governor
description: Track authoritative Codex allowance limits, sustainable pace, model/workflow efficiency, local history, and projected exhaustion. Use when the user asks about Codex usage, reset timing, plan value, model value, work-block consumption, or invokes the Codex Usage Governor.
---

# Codex Usage Governor

Use the deterministic `governor.py` script as the sole authority for arithmetic and labels. Resolve the installed plugin root from this skill's location: the script is at `../../scripts/governor.py`. Store data in the plugin data directory when available; otherwise use the script's default under `~/.codex/usage-governor`.

The primary collector is Codex App Server `account/rateLimits/read`. Session JSONL is a compatibility fallback only. Do not estimate the account limit from token totals.

## Workflow

1. Run `collect` before an on-demand report so the latest completed local Codex sessions are included.
2. Run exactly one requested report command.
3. Present stdout without altering numeric values.
4. Preserve the script's `OBSERVED`, `ESTIMATED`, and `PROJECTED` labels.
5. Never block work or automatically change models.

## Commands

From the skill directory, use Python 3 with these arguments:

- Status: `python ../../scripts/governor.py collect`, then `python ../../scripts/governor.py report status`
- Today: `python ../../scripts/governor.py collect`, then `python ../../scripts/governor.py report today`
- Governing window: `python ../../scripts/governor.py collect`, then `python ../../scripts/governor.py report week`
- History: `python ../../scripts/governor.py collect`, then `python ../../scripts/governor.py report history`
- Configuration: `python ../../scripts/governor.py config [key] [value]`
- Compact PowerShell/footer view: `python ../../scripts/governor.py collect`, then `python ../../scripts/governor.py report compact`
- Install automatic PowerShell launching: run `../../scripts/cug.cmd shell-install`. Setup copies the live scripts to `~/.codex/usage-governor/runtime`, where plugin cache cleanup cannot break an open bar. Open a new PowerShell window once after setup. `codex` launches one Governor pane per Windows Terminal window, and `codex-raw` launches the original CLI.
- Remove automatic PowerShell launching: run `../../scripts/cug.cmd shell-remove`.
- Start a labeled work block: `python ../../scripts/governor.py work start --model <model> --reasoning <effort> --category <category> [--note <note>]`
- Stop a work block: `python ../../scripts/governor.py work stop --outcome <accepted|partial|rework|failed> [--time-saved-hours <hours>] [--note <note>]`
- List raw completed work blocks: `python ../../scripts/governor.py work list`

If `python` is unavailable, retry with `python3`. If neither exists, state that Python 3 is required.

## Privacy and integrity

Collect only normalized rate-limit readings, reset timestamps, optional user-supplied work labels, model identifiers, plan type, session identifier, and token totals. Never persist prompts, responses, code, file contents, or command output. Read `references/data-contract.md` before changing collection or persistence behavior.
