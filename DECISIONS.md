# Architectural Decisions

## ADR-001 — Separate collection from budgeting

**Status:** Accepted

The usage collector will normalize Codex data into a provider-neutral schema. Forecasting and reporting will consume that schema rather than Codex-specific payloads directly.

This preserves the proven budgeting concepts while allowing Codex integration to evolve independently.

## ADR-002 — Deterministic arithmetic

**Status:** Accepted

All percentages, budgets, rates, confidence labels, and exhaustion projections will be produced by deterministic code. The skill may select a command and relay its output but must not recompute values.

## ADR-003 — No terminal scraping as the default architecture

**Status:** Accepted

The project will first seek structured app-server, hook, status, or account interfaces. Parsing rendered terminal output is brittle and locale-sensitive, so it may only be used as an explicitly labeled prototype fallback.

## ADR-004 — Local and privacy-minimal history

**Status:** Accepted

Persist timestamps, usage-window readings, reset timestamps, model identifiers, and derived configuration only. Never persist prompts, responses, code, file contents, or command output.

## ADR-005 — Session JSONL is the first Codex collector adapter

**Status:** Accepted with migration risk

Codex CLI 0.147.0 emits structured `event_msg` / `token_count` records containing `rate_limits`, including `used_percent`, `window_minutes`, and `resets_at`. The initial collector reads those records through the transcript path supplied to hooks and through the local sessions directory for on-demand bootstrap.

Codex documentation states that the transcript format is not a stable hook interface. All parsing therefore remains isolated in the collector layer, and normalized history is the budgeting engine's only input.

## ADR-006 — Longest Codex window governs the weekly budget

**Status:** Accepted

When multiple structured windows are present, choose the longest window with `limit_id = codex` for the sustainable weekly budget. Preserve other windows in normalized history for later independent constraint evaluation.

## ADR-007 — Defer comparative model advice

**Status:** Superseded by ADR-010

Record the active model, but do not claim that switching models will extend subscription runway until local evidence demonstrates how model selection affects the same allowance meter. This avoids importing Anthropic pricing assumptions into Codex.

## ADR-008 — App Server is the primary allowance source

**Status:** Accepted

Use the documented Codex App Server `account/rateLimits/read` method as the primary collector. It returns authoritative account percentages, window durations, reset timestamps, plan type, credit balance, and earned-reset availability. Keep session JSONL parsing as a compatibility fallback because transcript structure is not a stable hook interface.

## ADR-009 — Measure model value through labeled work blocks

**Status:** Accepted

The account meter does not attribute each percentage increment to an individual model or task. Capture allowance readings around user-labeled work blocks and record model, reasoning effort, workflow category, outcome, and estimated time saved. Treat these labels as user-supplied and require repeated samples before recommending a model or subscription tier.

## ADR-010: Separate workload advice from personal efficiency claims

**Status:** Accepted

Recommend Sol, Terra, or Luna from official model roles, task complexity, expected outcome, project signals, and current allowance pressure. Describe these choices as workload-fit advice. Reserve personal efficiency claims for repeated labeled work blocks with recorded outcomes.

## ADR-011: Require confirmation before applying recommendations

**Status:** Accepted

Render `[Apply]` as an OSC 8 terminal link to a local `cug://` handler. Accept allowlisted model IDs and reasoning levels plus validated plugin IDs. Show the user the full change and require confirmation before writing a launch preference or installing a plugin. Apply model changes on the next Codex launch.

## ADR-012: Keep task text out of storage

**Status:** Accepted

Pass a short task and outcome summary to the Advisor for the current calculation. Do not write that text to history, configuration, work blocks, or logs. Persist the selected model and reasoning level only after the user approves the Apply action.

## ADR-013: Run the pinned bar from a durable shell runtime

**Status:** Accepted

Copy the Governor scripts into `%USERPROFILE%\.codex\usage-governor\runtime` during shell setup. Launch the pinned pane from that directory so Codex can replace plugin cache folders without breaking a running bar.

Use a mutex scoped to `WT_SESSION` to allow one bar per Windows Terminal window. Clear the visible pane and scrollback before each two-line refresh.
