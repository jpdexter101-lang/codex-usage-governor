#!/usr/bin/env python3
"""Privacy-safe project/task advisor for Codex Usage Governor."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import urllib.parse

import governor

MODELS = {"gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna"}
REASONING = {"low", "medium", "high", "xhigh", "max"}

TOOL_RULES = [
    (("ui", "design", "frontend", "react", "expo", "mobile"), ("ui-ux-pro-max", "browser")),
    (("browser", "website", "web app", "e2e", "playwright"), ("browser",)),
    (("chrome", "extension", "logged in"), ("chrome",)),
    (("pdf",), ("pdf",)),
    (("spreadsheet", "excel", "csv", "data analysis"), ("spreadsheets",)),
    (("document", "word", "docx"), ("documents",)),
    (("slides", "presentation", "powerpoint"), ("presentations",)),
    (("chart", "visualization", "graph"), ("visualize",)),
    (("deploy", "hosting", "website"), ("sites",)),
    (("calendar", "schedule"), ("google-calendar",)),
    (("slack",), ("slack",)),
    (("google drive",), ("google-drive",)),
]

AVAILABLE_PLUGINS = {
    "ui-ux-pro-max": "ui-ux-pro-max@ui-ux-pro-max-skill",
    "browser": "browser@openai-bundled", "chrome": "chrome@openai-bundled",
    "pdf": "pdf@openai-primary-runtime", "spreadsheets": "spreadsheets@openai-primary-runtime",
    "documents": "documents@openai-primary-runtime", "presentations": "presentations@openai-primary-runtime",
    "visualize": "visualize@openai-bundled", "sites": "sites@openai-bundled",
    "google-calendar": "google-calendar@openai-curated", "slack": "slack@openai-curated",
    "google-drive": "google-drive@openai-curated",
}


def installed_tools(codex_home: Path) -> set[str]:
    names: set[str] = set()
    roots = [codex_home / "plugins" / "cache", codex_home / "skills"]
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("SKILL.md"):
            names.add(path.parent.name.lower())
        for path in root.rglob("plugin.json"):
            try:
                names.add(str(json.loads(path.read_text(encoding="utf-8"))["name"]).lower())
            except (OSError, KeyError, json.JSONDecodeError):
                pass
    return names


def project_text(project: Path) -> str:
    names: list[str] = [project.name]
    markers = ("package.json", "app.json", "pyproject.toml", "requirements.txt", "docker-compose.yml", "Cargo.toml", "pubspec.yaml")
    for marker in markers:
        path = project / marker
        if path.exists():
            names.append(marker)
            try:
                names.append(path.read_text(encoding="utf-8", errors="ignore")[:12000])
            except OSError:
                pass
    return " ".join(names).lower()


def recommend(status: dict | None, project: Path, task: str, outcome: str, tools: set[str]) -> dict:
    text = " ".join((project_text(project), task, outcome)).lower()
    high_stakes = any(word in text for word in ("security", "production", "payment", "migration", "architecture", "release", "data loss", "legal", "medical"))
    complex_work = any(word in text for word in ("debug", "refactor", "build app", "implement", "integration", "multi-step", "root cause", "performance"))
    light_work = any(word in text for word in ("dnd", "d&d", "character", "campaign", "readme", "copy edit", "rename", "small edit", "format", "brainstorm"))

    if high_stakes:
        model, reasoning, why = "gpt-5.6-sol", "high", "The outcome needs extra checking and stronger reasoning."
    elif complex_work:
        model, reasoning, why = "gpt-5.6-terra", "high", "Terra should balance careful implementation with allowance use."
    elif light_work:
        model, reasoning, why = "gpt-5.6-luna", "medium", "Luna should handle this comfortably and preserve your allowance."
    else:
        model, reasoning, why = "gpt-5.6-terra", "medium", "Terra is a solid middle ground for this project."

    pressure = status.get("status") if status else None
    remaining = float(status.get("remaining_percent", 100)) if status else 100
    if pressure == "RED" or remaining < 25:
        original_model = model
        if model == "gpt-5.6-sol" and not high_stakes:
            model = "gpt-5.6-terra"
        elif model == "gpt-5.6-terra" and not complex_work and not high_stakes:
            model = "gpt-5.6-luna"
        if model != original_model:
            why = f"{model.removeprefix('gpt-5.6-').title()} fits this task and preserves more allowance."

    matched: list[str] = []
    for keywords, candidates in TOOL_RULES:
        if any(keyword in text for keyword in keywords):
            for candidate in candidates:
                if (candidate in tools or candidate in AVAILABLE_PLUGINS) and candidate not in matched:
                    matched.append(candidate)

    selected_tools = matched[:3]
    installs = [AVAILABLE_PLUGINS[name] for name in selected_tools if name not in tools and name in AVAILABLE_PLUGINS]
    return {"model": model, "reasoning": reasoning, "tools": selected_tools, "install": installs, "why": why}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir")
    parser.add_argument("--project", default=os.getcwd())
    parser.add_argument("--task", default="")
    parser.add_argument("--outcome", default="")
    parser.add_argument("--bar", action="store_true")
    args = parser.parse_args()
    root, history_path, config_path, _ = governor.data_paths(args.data_dir)
    status = governor.compute(governor.read_history(history_path), governor.load_config(root, config_path))
    codex_home = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    choice = recommend(status, Path(args.project), args.task, args.outcome, installed_tools(codex_home))
    query = urllib.parse.urlencode({"model": choice["model"], "reasoning": choice["reasoning"], "plugins": ",".join(choice["install"])})
    link = f"cug://apply?{query}"
    if args.bar:
        apply_link = f"\033]8;;{link}\033\\[Apply]\033]8;;\033\\"
        print(f"Advisor {choice['model'].removeprefix('gpt-5.6-').title()}/{choice['reasoning']} | {apply_link}", end="", flush=True)
    else:
        print(json.dumps({**choice, "apply_uri": link}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
