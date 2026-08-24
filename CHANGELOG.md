# Changelog

## 0.2.0 — Unreleased

- Added a Task Advisor that recommends Sol, Terra, or Luna plus reasoning effort from project type, task complexity, expected outcome, and allowance pressure.
- Added clickable, confirmed Apply links for future launch settings and missing plugin installation.
- Kept the pinned Advisor line compact: model, reasoning, and Apply only.
- Fixed refresh scrolling that left repeated usage rows and stale Advisor text in the pane.
- Prevented duplicate Governor panes after Codex updates or profile reloads with a per-terminal single-instance lock.

- Made Codex App Server `account/rateLimits/read` the primary authoritative collector.
- Retained session JSONL parsing as a compatibility fallback.
- Added normalized credit balance and earned-reset availability fields.
- Added labeled work blocks for model, reasoning, category, outcome, and time-saved analysis.
- Added compact reporting plus the PowerShell `cug.ps1` workflow and Windows `cug.cmd` launcher.
- Recorded and live-verified the post-earned-reset experiment from 1% through 3% used.
- Expanded the automated suite to six passing tests.
- Added a Windows Terminal launcher that pins an automatically refreshing one-line decision bar below Codex.
- Added remaining allowance, daily use/budget, active model, pace status, burn rate, and exhaustion/reset guidance to the ambient bar.
- Added managed PowerShell integration so `codex` opens the Governor in the current Windows Terminal tab, with `codex-raw` as an explicit bypass.

## 0.1.0 — Unreleased

- Created the Codex Usage Governor project workspace.
- Added the initial Codex plugin and reusable skill scaffolds.
- Defined product principles, milestones, privacy boundaries, and collector-first architecture.
- Added structured collection from Codex `token_count` session events.
- Added normalized, append-only local usage history with content exclusion.
- Added deterministic status, today, governing-window, history, and configuration reports.
- Added EWMA burn-rate estimation, sustainable daily budgets, and exhaustion projections.
- Added automatic `SessionStart` initialization and `Stop` sampling hooks.
- Added five passing unit tests and completed a live local collection against Codex CLI 0.147.0.
- Verified authoritative live allowance collection through Codex App Server on CLI 0.149.0.
- Recorded the post-earned-reset Plus baseline at 1% used with a seven-day reset window.
- Added the Codex value experiment and PowerShell-first measurement roadmap.
