# Current State

## Status

PowerShell-first 0.2.0 public beta installed, live-tested, and published. The Task Advisor and clickable Apply flow work locally.

## Created

- Project documentation workspace
- Codex plugin manifest
- `usage-governor` skill scaffold with initial operating rules
- Plugin directories for hooks and deterministic scripts
- Structured session JSONL collector
- Privacy-minimal append-only history
- Sustainable-rate and burn-rate reporting engine
- Session-start and stop hooks
- Ten automated tests
- Authoritative Codex App Server collector
- PowerShell `cug` status, watch, launcher, and labeled-work commands
- Post-earned-reset experiment baseline and runtime history
- Same-tab Windows Terminal launcher with a pinned two-line pane
- Managed `codex` and `codex-raw` PowerShell functions
- Project-aware and task-aware model recommendations
- Installed skill and plugin suggestions
- Confirmed `cug://` Apply links for launch settings and plugin installation
- Durable shell runtime outside the disposable plugin cache
- One Governor pane per Windows Terminal window
- Two-line refresh that clears old readings from scrollback
- Public GitHub repository at `jpdexter101-lang/codex-usage-governor`

## Confirmed Codex capabilities

- Interactive daily, weekly, and cumulative usage views
- Session status with rate limits
- Configurable status-line rate-limit and token fields
- Lifecycle hooks, including session start, stop, and session end

## Verified locally

- Codex CLI 0.147.0 writes `token_count` events containing `rate_limits`.
- The local Plus account exposed a seven-day, 10,080-minute Codex window with authoritative usage percentage and reset timestamp.
- A live collection produced a complete report using only normalized usage metadata.
- Stored rows contain no prompt or response fields.
- Codex CLI 0.149.0 App Server returned the live Plus allowance through `account/rateLimits/read`.
- The Windows launcher reported movement from 1% at the post-reset baseline to 3% during implementation.
- Ten automated tests pass, including App Server normalization and Advisor decisions.
- A D&D planning task recommends Luna with friendly allowance guidance.
- A production payment migration keeps Sol/high under allowance pressure.
- The registered Apply handler saved a Luna/medium next-launch preference during the live click test.

## Open technical risks

- App Server is still exposed through an experimental CLI command, so protocol changes remain a compatibility risk.
- Only the currently observed Plus-plan weekly window has been exercised live; secondary windows and other plans need fixtures or live samples.
- Task recommendations use workload fit and current pressure. Personalized model-value claims still need labeled work-block evidence.
- Official plugin validators cannot run in the current Python environment until their `PyYAML` dependency is available.
- Codex must start a new session to load a changed model or a newly installed plugin.
- Existing terminals must close once after a shell-integration upgrade so PowerShell loads the new managed function.

## Next action

Collect labeled work blocks across Sol, Terra, and Luna. Use the results to tune recommendations around accepted outcomes and allowance cost.
