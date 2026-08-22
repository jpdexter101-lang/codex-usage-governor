# Usage Data Contract

Collectors must normalize account usage into records with these conceptual fields:

- `observed_at`: timestamp of the reading
- `source`: structured Codex interface used
- `windows[]`: window name, used percentage, and reset timestamp
- `model`: active model identifier when available
- `session_id`: optional opaque session identifier
- `tokens`: optional input/output/cached token counters
- `reset_credits_available`: optional authoritative earned-reset count
- `credit_balance`: optional authoritative purchased/workspace credit balance

Completed work blocks may also store user-supplied model, reasoning effort, workflow category, outcome, estimated time saved, and short notes. These are labels, not observed account facts.

Only fields supplied directly by Codex are observed facts. Locally calculated rates, ratios, runway, and exhaustion times are estimates or projections.

Reject readings that lack a timestamp, contain percentages outside 0–100, or cross a reset boundary without starting a new window series.
