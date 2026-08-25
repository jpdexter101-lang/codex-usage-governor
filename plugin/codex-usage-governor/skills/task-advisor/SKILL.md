---
name: task-advisor
description: Recommend a Codex model, reasoning effort, installed plugins, and skills for the current task using its complexity, expected outcome, project type, and current allowance pressure. Use when a user starts, scopes, or changes a task or project and a cheaper or better-equipped workflow could help.
---

# Codex Task Advisor

Give the user a brief recommendation when the current model looks excessive, too weak, or misses a useful installed tool. Keep the tone friendly. Say what should work and why. Do not shame the user for spending allowance.

Keep the pinned bar to `Advisor <model>/<reasoning> | [Apply]`. Put explanations and tool suggestions in the full `recommend` output.

Resolve the plugin root from this skill directory. Run `python ../../scripts/advisor.py --task <current request summary> --outcome <expected result> --project <working directory>`. The script is the authority for model, reasoning, and tool names.

Do not persist the user's request. The script receives it for the current calculation only. Do not switch models, install plugins, or change settings without the user's click or explicit approval.

Skip the recommendation when it would repeat the current setup without adding useful information. Mention that model changes apply on the next launch. Installed matching skills need no activation; Codex invokes them from their descriptions.
