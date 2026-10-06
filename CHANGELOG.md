# Changelog

## 0.2.0 — Unreleased

- Added orphan cloud-bridge detection: flags long-lived `codex.exe exec-server --remote ...` processes (Codex Cloud environment bridges) that can silently keep consuming usage with no interactive CLI session open to trigger a hook-based reading. Surfaces as a red warning line above the bar/status output; threshold configurable via `orphan_bridge_threshold_hours` (default 1h). Born from a real incident: one sat open ~69 hours unnoticed after a failed task silently resumed when the usage limit reset.
- Added a Task Advisor that recommends Sol, Terra, or Luna plus reasoning effort from project type, task complexity, expected outcome, and allowance pressure.
- Added clickable, confirmed Apply links for future launch settings and missing plugin installation.
- Kept the pinned Advisor line compact: model, reasoning, and Apply only.
- Fixed refresh scrolling that left repeated usage rows and stale Advisor text in the pane.
- Prevented duplicate Governor panes after Codex updates or profile reloads with a per-terminal single-instance lock.
- Moved the live bar to a durable runtime so plugin cache cleanup cannot break an open pane.
- Cleared the pane scrollback on refresh so old readings do not accumulate behind the current two lines.

- Made Codex App Server `account/rateLimits/read` the primary authoritative collector.
- Retained session JSONL parsing as a compatibility fallback.
- Added normalized credit balance and earned-reset availability fields.
- Added labeled work blocks for model, reasoning, category, outcome, and time-saved analysis.
- Added compact reporting plus the PowerShell `cug.ps1` workflow and Windows `cug.cmd` launcher.
- Recorded and live-verified the post-earned-reset experiment from 1% through 3% used.
- Expanded the automated suite to six passing tests.
- Added a Windows Terminal launcher that pins an automatically refreshing two-line decision bar below Codex.
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
