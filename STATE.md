# Current State

## Status

PowerShell-first 0.2.0 collector implemented and live-tested; installation and extended work-block sampling are next.

## Created

- Project documentation workspace
- Codex plugin manifest
- `usage-governor` skill scaffold with initial operating rules
- Plugin directories for hooks and deterministic scripts
- Structured session JSONL collector
- Privacy-minimal append-only history
- Sustainable-rate and burn-rate reporting engine
- Session-start and stop hooks
- Five automated tests
- Authoritative Codex App Server collector
- PowerShell `cug` status, watch, launcher, and labeled-work commands
- Post-earned-reset experiment baseline and runtime history

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
- Six automated tests pass, including normalization of the documented App Server response.

## Open technical risks

- App Server is still exposed through an experimental CLI command, so protocol changes remain a compatibility risk.
- Only the currently observed Plus-plan weekly window has been exercised live; secondary windows and other plans need fixtures or live samples.
- Comparative model advice is deferred until there is defensible evidence that model changes correlate with the same allowance meter.
- Official plugin validators cannot run in the current Python environment until their `PyYAML` dependency is available.

## Next action

Create or connect a local marketplace entry, install and trust the plugin hooks, then collect labeled work blocks across models and reasoning levels.
