# TODO

## Milestone 1 — Usage collector proof

- [x] Record installed Codex version and authentication mode.
- [x] Inspect documented app-server and hook payload schemas for rate-limit data.
- [x] Capture redacted sample payloads.
- [x] Decide collector approach and document fallback behavior.
- [x] Prove authoritative collection through Codex App Server `account/rateLimits/read`.
- [x] Replace session-JSONL collection as the primary adapter with App Server collection.

## Milestone 2 — Deterministic core

- [x] Define provider-neutral usage-window schema.
- [x] Port sustainable daily budget calculations.
- [x] Port rollover and borrowing behavior.
- [x] Implement burn-rate estimation with confidence thresholds.
- [x] Add initial synthetic fixtures for normalization, privacy, pacing, and idempotency.
- [ ] Expand fixtures across reset boundaries, multiple limit IDs, and secondary windows.

## Milestone 3 — Codex integration

- [x] Implement lifecycle hooks.
- [x] Implement status, today, week, history, and config commands.
- [x] Implement explicit work-block commands.
- [x] Add the supported native rate-limit fields to the Codex status line.
- [ ] Validate Windows, macOS, and Linux paths.

## Milestone 3A — PowerShell workflow

- [x] Add a `cug` PowerShell command with compact, status, today, week, and watch views.
- [x] Add a `cug codex` launcher that captures before/after allowance readings.
- [x] Add a pinned Windows Terminal Governor pane.
- [x] Make `codex` launch the Governor in the current tab.
- [x] Keep the live bar outside disposable plugin cache folders.
- [x] Prevent duplicate bars within one Windows Terminal window.
- [x] Clear old refresh output from the pane scrollback.
- [ ] Cache live readings briefly so prompt rendering does not repeatedly start App Server.
- [x] Record model, reasoning effort, workflow label, and accepted outcome around work blocks.

## Milestone 3B: Task Advisor

- [x] Recommend Sol, Terra, or Luna from task complexity and expected outcome.
- [x] Adjust recommendations when allowance pace runs high.
- [x] Suggest matching installed skills and plugins.
- [x] Offer known missing plugins through a confirmed Apply action.
- [x] Save model and reasoning preferences for the next Codex launch.
- [x] Register and remove the local `cug://` handler through shell setup.
- [ ] Learn from repeated labeled work-block outcomes.
- [ ] Add a compact explanation view for narrow terminal panes.

## Milestone 4 — Product hardening

- [ ] Test multiple concurrent Codex sessions.
- [ ] Verify history never stores prompt or code content.
- [x] Document installation and removal.
- [x] Package and install the plugin through the personal marketplace.
- [x] Add a workload-fit model advisor with clear limits on personalized claims.
- [x] Publish the public beta on GitHub.
- [ ] Produce Plus-versus-Pro and Codex-versus-Claude monthly decision reports.
