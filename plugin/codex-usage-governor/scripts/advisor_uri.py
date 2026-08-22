#!/usr/bin/env python3
"""Handle allowlisted cug:// recommendation actions on Windows."""

from __future__ import annotations

import ctypes
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import urllib.parse

MODELS = {"gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna"}
REASONING = {"low", "medium", "high", "xhigh", "max"}
PLUGIN_ID = re.compile(r"^[A-Za-z0-9_.-]+@[A-Za-z0-9_.-]+$")


def message(text: str, flags: int) -> int:
    return ctypes.windll.user32.MessageBoxW(None, text, "Codex Usage Governor", flags)


def main(uri: str) -> int:
    parsed = urllib.parse.urlparse(uri)
    if parsed.scheme != "cug" or parsed.netloc != "apply":
        return 2
    values = urllib.parse.parse_qs(parsed.query)
    model = values.get("model", [""])[0]
    reasoning = values.get("reasoning", [""])[0]
    plugin_ids = [value for value in values.get("plugins", [""])[0].split(",") if value]
    if model not in MODELS or reasoning not in REASONING:
        message("The recommendation link contains an unsupported model or reasoning level.", 0x10)
        return 2
    if any(not PLUGIN_ID.fullmatch(value) for value in plugin_ids):
        message("The recommendation contains an invalid plugin ID.", 0x10)
        return 2
    details = f"Model: {model}\nReasoning: {reasoning}"
    if plugin_ids:
        details += "\nInstall: " + ", ".join(plugin_ids)
    if message("Apply this setup for future Codex launches?\n\n" + details, 0x21) != 1:
        return 0
    data = Path.home() / ".codex" / "usage-governor"
    data.mkdir(parents=True, exist_ok=True)
    preference = data / "launch-preference.json"
    preference.write_text(json.dumps({"model": model, "reasoning": reasoning}, indent=2) + "\n", encoding="utf-8")
    codex = shutil.which("codex.exe") or shutil.which("codex")
    for plugin_id in plugin_ids:
        if codex:
            subprocess.run([codex, "plugin", "add", plugin_id], check=False, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    message("Saved. The model and reasoning level will apply the next time you launch Codex.", 0x40)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]) if len(sys.argv) == 2 else 2)
