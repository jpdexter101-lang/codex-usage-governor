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
- [ ] Implement explicit work-horizon commands.
- [ ] Add optional status-line integration where supported.
- [ ] Validate Windows, macOS, and Linux paths.

## Milestone 3A — PowerShell workflow

- [x] Add a `cug` PowerShell command with compact, status, today, week, and watch views.
- [x] Add a `cug codex` launcher that captures before/after allowance readings.
- [ ] Add optional Windows Terminal title and PowerShell prompt summaries.
- [ ] Cache live readings briefly so prompt rendering does not repeatedly start App Server.
- [x] Record model, reasoning effort, workflow label, and accepted outcome around work blocks.

## Milestone 4 — Product hardening

- [ ] Test multiple concurrent Codex sessions.
- [ ] Verify history never stores prompt or code content.
- [ ] Document installation and removal.
- [ ] Package and validate the plugin.
- [ ] Add a model advisor only after model-to-meter behavior is evidence-backed.
- [ ] Produce Plus-versus-Pro and Codex-versus-Claude monthly decision reports.
