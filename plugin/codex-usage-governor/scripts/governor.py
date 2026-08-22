#!/usr/bin/env python3
"""Codex Usage Governor.

Collect authoritative account rate limits from Codex App Server and turn them
into deterministic, advisory pacing reports. Session JSONL remains a fallback.
Standard library only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import threading
import time


DEFAULT_CONFIG = {
    "yellow_threshold_pct": 75.0,
    "min_burn_data_hours": 0.25,
    "ewma_half_life_hours": 0.75,
}


def data_paths(data_dir: str | None) -> tuple[Path, Path, Path, Path]:
    root = Path(data_dir or os.environ.get("PLUGIN_DATA") or Path.home() / ".codex" / "usage-governor")
    return root, root / "history.jsonl", root / "config.json", root / "work_horizon.json"


def ensure(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)


def load_config(root: Path, path: Path) -> dict:
    ensure(root)
    if not path.exists():
        save_json(path, DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        value = {}
    return {**DEFAULT_CONFIG, **{k: value[k] for k in DEFAULT_CONFIG if k in value}}


def save_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def read_history(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return sorted(rows, key=lambda row: row.get("observed_at", 0))


def append_rows(path: Path, rows: list[dict]) -> int:
    if not rows:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = read_history(path)
    seen = {row.get("event_key") for row in existing}
    fresh = [row for row in rows if row.get("event_key") not in seen]
    with path.open("a", encoding="utf-8") as handle:
        for row in fresh:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    return len(fresh)


def append_jsonl(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, sort_keys=True) + "\n")


def parse_timestamp(value: object, fallback: float) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
        except ValueError:
            pass
    return fallback


def normalize_limits(raw: dict) -> list[dict]:
    limits: list[dict] = []
    limit_id = raw.get("limit_id") or "codex"
    for lane in ("primary", "secondary"):
        window = raw.get(lane)
        if not isinstance(window, dict):
            continue
        used = window.get("used_percent")
        minutes = window.get("window_minutes")
        resets_at = window.get("resets_at")
        if not all(isinstance(value, (int, float)) for value in (used, minutes, resets_at)):
            continue
        if not 0 <= float(used) <= 100 or float(minutes) <= 0:
            continue
        limits.append({
            "id": str(limit_id),
            "lane": lane,
            "used_percent": float(used),
            "window_minutes": int(minutes),
            "resets_at": float(resets_at),
        })
    return limits


def _pick(value: dict, snake: str, camel: str) -> object:
    return value.get(snake) if snake in value else value.get(camel)


def normalize_app_server_bucket(raw: dict) -> list[dict]:
    """Normalize one account/rateLimits/read bucket."""
    limits: list[dict] = []
    limit_id = _pick(raw, "limit_id", "limitId") or "codex"
    for lane in ("primary", "secondary"):
        window = raw.get(lane)
        if not isinstance(window, dict):
            continue
        used = _pick(window, "used_percent", "usedPercent")
        minutes = _pick(window, "window_minutes", "windowDurationMins")
        resets_at = _pick(window, "resets_at", "resetsAt")
        if not all(isinstance(value, (int, float)) for value in (used, minutes, resets_at)):
            continue
        if not 0 <= float(used) <= 100 or float(minutes) <= 0:
            continue
        limits.append({
            "id": str(limit_id),
            "lane": lane,
            "used_percent": float(used),
            "window_minutes": int(minutes),
            "resets_at": float(resets_at),
        })
    return limits


def records_from_rate_limit_result(result: dict, observed_at: float | None = None) -> list[dict]:
    """Convert the documented App Server response into privacy-minimal rows."""
    observed_at = float(observed_at or time.time())
    buckets = result.get("rateLimitsByLimitId") or result.get("rate_limits_by_limit_id")
    if not isinstance(buckets, dict) or not buckets:
        single = result.get("rateLimits") or result.get("rate_limits")
        buckets = {str(_pick(single, "limit_id", "limitId") or "codex"): single} if isinstance(single, dict) else {}
    rows: list[dict] = []
    reset_info = result.get("rateLimitResetCredits") or result.get("rate_limit_reset_credits") or {}
    reset_count = _pick(reset_info, "available_count", "availableCount") if isinstance(reset_info, dict) else None
    for bucket_id, bucket in buckets.items():
        if not isinstance(bucket, dict):
            continue
        limits = normalize_app_server_bucket(bucket)
        if not limits:
            continue
        plan_type = _pick(bucket, "plan_type", "planType")
        credits = bucket.get("credits") if isinstance(bucket.get("credits"), dict) else {}
        balance = credits.get("balance")
        fingerprint = ",".join(f"{w['lane']}:{w['used_percent']}:{int(w['resets_at'])}" for w in limits)
        rows.append({
            "event_key": f"app-server:{int(observed_at * 1000)}:{bucket_id}:{fingerprint}",
            "observed_at": observed_at,
            "source": "codex-app-server",
            "session_id": None,
            "model": None,
            "plan_type": str(plan_type) if plan_type is not None else None,
            "limits": limits,
            "tokens": None,
            "reset_credits_available": int(reset_count) if isinstance(reset_count, (int, float)) else None,
            "credit_balance": str(balance) if balance is not None else None,
        })
    return rows


def collect_app_server(timeout: float = 10.0) -> list[dict]:
    """Read current ChatGPT/Codex limits from a short-lived local App Server."""
    executable = shutil.which("codex")
    if not executable:
        return []
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        process = subprocess.Popen(
            [executable, "app-server"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace",
            bufsize=1, creationflags=creationflags,
        )
    except OSError:
        return []
    output: queue.Queue[str | None] = queue.Queue()

    def reader() -> None:
        assert process.stdout is not None
        for line in process.stdout:
            output.put(line)
        output.put(None)

    threading.Thread(target=reader, daemon=True).start()
    messages = [
        {"method": "initialize", "id": 0, "params": {"clientInfo": {
            "name": "codex_usage_governor", "title": "Codex Usage Governor", "version": "0.2.0"}}},
        {"method": "initialized", "params": {}},
        {"method": "account/rateLimits/read", "id": 2},
    ]
    try:
        assert process.stdin is not None
        for message in messages:
            process.stdin.write(json.dumps(message, separators=(",", ":")) + "\n")
        process.stdin.flush()
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                line = output.get(timeout=max(0.05, deadline - time.monotonic()))
            except queue.Empty:
                break
            if line is None:
                break
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                continue
            if message.get("id") == 2:
                result = message.get("result")
                return records_from_rate_limit_result(result) if isinstance(result, dict) else []
    finally:
        try:
            process.terminate()
            process.wait(timeout=2)
        except (OSError, subprocess.TimeoutExpired):
            process.kill()
    return []


def collect_file(path: Path, model_hint: str | None = None) -> list[dict]:
    records: list[dict] = []
    model = model_hint
    session_id = path.stem
    try:
        lines = path.open("r", encoding="utf-8", errors="replace")
    except OSError:
        return records
    with lines:
        for number, line in enumerate(lines, 1):
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "session_meta":
                session_id = str((event.get("payload") or {}).get("id") or session_id)
            payload = event.get("payload") or {}
            if event.get("type") == "turn_context" and payload.get("model"):
                model = str(payload["model"])
            if event.get("type") != "event_msg" or payload.get("type") != "token_count":
                continue
            raw_limits = payload.get("rate_limits")
            limits = normalize_limits(raw_limits) if isinstance(raw_limits, dict) else []
            if not limits:
                continue
            observed_at = parse_timestamp(event.get("timestamp"), path.stat().st_mtime)
            info = payload.get("info") or {}
            tokens = info.get("total_token_usage") if isinstance(info, dict) else None
            records.append({
                "event_key": f"{session_id}:{number}",
                "observed_at": observed_at,
                "source": "codex-session-jsonl",
                "session_id": session_id,
                "model": model,
                "plan_type": raw_limits.get("plan_type"),
                "limits": limits,
                "tokens": tokens if isinstance(tokens, dict) else None,
            })
    return records


def sessions_root(value: str | None) -> Path:
    if value:
        return Path(value)
    codex_home = os.environ.get("CODEX_HOME")
    return Path(codex_home) / "sessions" if codex_home else Path.home() / ".codex" / "sessions"


def collect_sessions(transcript: str | None, sessions_dir: str | None, model: str | None) -> list[dict]:
    if transcript:
        return collect_file(Path(transcript), model)
    root = sessions_root(sessions_dir)
    files = sorted(root.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:100] if root.exists() else []
    rows: list[dict] = []
    for path in files:
        found = collect_file(path, model)
        if found:
            rows.append(found[-1])
    return sorted(rows, key=lambda row: row["observed_at"])


def latest_session_model(sessions_dir: str | None) -> str | None:
    root = sessions_root(sessions_dir)
    if not root.exists():
        return None
    try:
        files = sorted(root.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
    except OSError:
        return None
    for path in files:
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line in reversed(lines[-500:]):
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            payload = event.get("payload") or {}
            if event.get("type") == "turn_context" and payload.get("model"):
                return str(payload["model"])
    return None


def collect(transcript: str | None, sessions_dir: str | None, model: str | None) -> list[dict]:
    """Prefer the supported account surface; use transcripts only as fallback."""
    live = collect_app_server()
    if live:
        model_hint = model or latest_session_model(sessions_dir)
        for row in live:
            row["model"] = model_hint
        return live
    return collect_sessions(transcript, sessions_dir, model)


def get_window(row: dict, window_id: str, lane: str, reset: float | None = None) -> dict | None:
    for window in row.get("limits") or []:
        if window.get("id") == window_id and window.get("lane") == lane:
            if reset is None or window.get("resets_at") == reset:
                return window
    return None


def latest_governing_window(rows: list[dict]) -> tuple[dict, dict] | None:
    candidates: list[tuple[int, float, dict, dict]] = []
    for row in rows:
        for window in row.get("limits") or []:
            if window.get("id") == "codex":
                candidates.append((int(window["window_minutes"]), row["observed_at"], row, window))
    if not candidates:
        for row in rows:
            for window in row.get("limits") or []:
                candidates.append((int(window["window_minutes"]), row["observed_at"], row, window))
    if not candidates:
        return None
    _, _, row, window = max(candidates, key=lambda item: (item[0], item[1]))
    return row, window


def local_midnight(epoch: float) -> float:
    stamp = dt.datetime.fromtimestamp(epoch).astimezone()
    return stamp.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()


def ewma_rate(rows: list[dict], target: dict, now: float, config: dict) -> tuple[float | None, float]:
    points: list[tuple[float, float]] = []
    for row in rows:
        window = get_window(row, target["id"], target["lane"], target["resets_at"])
        if window:
            points.append((float(row["observed_at"]), float(window["used_percent"])))
    points.sort()
    weighted_delta = weighted_hours = total_hours = 0.0
    half_life = float(config["ewma_half_life_hours"])
    for previous, current in zip(points, points[1:]):
        hours = (current[0] - previous[0]) / 3600
        if hours <= 0:
            continue
        delta = max(0.0, current[1] - previous[1])
        age_hours = max(0.0, (now - current[0]) / 3600)
        weight = 2 ** (-age_hours / half_life) if half_life > 0 else 1.0
        weighted_delta += delta * weight
        weighted_hours += hours * weight
        total_hours += hours
    if total_hours < float(config["min_burn_data_hours"]) or weighted_hours <= 0:
        return None, total_hours
    return weighted_delta / weighted_hours, total_hours


def compute(rows: list[dict], config: dict, now: float | None = None) -> dict | None:
    selected = latest_governing_window(rows)
    if not selected:
        return None
    latest_row, window = selected
    now = float(now or time.time())
    remaining = max(0.0, 100.0 - float(window["used_percent"]))
    remaining_seconds = max(0.0, float(window["resets_at"]) - now)
    remaining_days = max(remaining_seconds / 86400, 1 / 1440)
    sustainable_day = remaining / remaining_days
    day_start = local_midnight(now)
    same_window: list[tuple[dict, dict]] = []
    for row in rows:
        found = get_window(row, window["id"], window["lane"], window["resets_at"])
        if found:
            same_window.append((row, found))
    before_today = [item for item in same_window if item[0]["observed_at"] < day_start]
    today = [item for item in same_window if item[0]["observed_at"] >= day_start]
    baseline_used = float(before_today[-1][1]["used_percent"]) if before_today else (float(today[0][1]["used_percent"]) if today else float(window["used_percent"]))
    used_today = max(0.0, float(window["used_percent"]) - baseline_used)
    baseline_remaining = max(0.0, 100.0 - baseline_used)
    budget_start = max(day_start, now - int(window["window_minutes"]) * 60)
    days_at_start = max((float(window["resets_at"]) - budget_start) / 86400, 1 / 1440)
    today_budget = baseline_remaining / days_at_start
    today_remaining = today_budget - used_today
    pct_budget = 100.0 * used_today / today_budget if today_budget > 0 else 100.0
    rate, evidence_hours = ewma_rate(rows, window, now, config)
    projected_exhaustion = now + remaining / rate * 3600 if rate and rate > 0 else None
    if rate and projected_exhaustion < float(window["resets_at"]):
        status = "RED"
    elif pct_budget >= float(config["yellow_threshold_pct"]):
        status = "YELLOW"
    else:
        status = "GREEN"
    return {
        "observed_at": latest_row["observed_at"], "model": latest_row.get("model"),
        "plan_type": latest_row.get("plan_type"), "window": window,
        "remaining_percent": remaining, "remaining_seconds": remaining_seconds,
        "sustainable_percent_per_day": sustainable_day, "used_today": used_today,
        "today_budget": today_budget, "today_remaining": today_remaining,
        "today_budget_used_percent": pct_budget, "burn_rate_percent_per_hour": rate,
        "burn_evidence_hours": evidence_hours, "projected_exhaustion": projected_exhaustion,
        "status": status,
    }


def fmt_time(epoch: float | None) -> str:
    if epoch is None:
        return "--"
    value = dt.datetime.fromtimestamp(epoch).astimezone()
    return value.strftime("%a %Y-%m-%d %I:%M %p").replace(" 0", " ")


def fmt_duration(seconds: float) -> str:
    seconds = max(0, int(seconds)); days, rem = divmod(seconds, 86400); hours, rem = divmod(rem, 3600); minutes = rem // 60
    return " ".join(([f"{days}d"] if days else []) + ([f"{hours}h"] if hours or days else []) + [f"{minutes}m"])


def fmt_short_time(epoch: float) -> str:
    value = dt.datetime.fromtimestamp(epoch).astimezone()
    return value.strftime("%a %I:%M %p").replace(" 0", " ")


def print_status(status: dict, config: dict, mode: str) -> None:
    if mode == "bar":
        colors = {"GREEN": "\033[92m", "YELLOW": "\033[93m", "RED": "\033[91m"}
        labels = {"GREEN": "SAFE", "YELLOW": "PACE", "RED": "HIGH"}
        reset = fmt_short_time(status["window"]["resets_at"])
        rate = status["burn_rate_percent_per_hour"]
        if rate is None:
            runway = f"reset {reset} / learning pace"
        elif status["projected_exhaustion"] and status["projected_exhaustion"] < status["window"]["resets_at"]:
            when = fmt_short_time(status["projected_exhaustion"])
            runway = f"{rate:.2f}%/h / out {when}"
        else:
            runway = f"{rate:.2f}%/h / lasts to {reset}"
        color = colors[status["status"]]
        label = labels[status["status"]]
        print(
            f"Codex {status['remaining_percent']:.0f}% left  |  "
            f"Today {status['used_today']:.1f}/{status['today_budget']:.1f}%  |  "
            f"{status['model'] or 'model unknown'}  |  {color}[{label}]\033[0m  |  {runway}"
        )
        return
    if mode == "compact":
        icon = {"GREEN": "OK", "YELLOW": "PACE", "RED": "HIGH"}[status["status"]]
        print(
            f"CODEX {status['remaining_percent']:.0f}% left | "
            f"reset {fmt_time(status['window']['resets_at'])} | {icon}"
        )
        return
    if mode == "today":
        print("Codex Usage Governor — Today")
        print(f"OBSERVED used today: {status['used_today']:.1f}%")
        print(f"PROJECTED sustainable budget: {status['today_budget']:.1f}%")
        print(f"PROJECTED remaining today: {status['today_remaining']:.1f}%")
        print(f"Status: {status['status']}")
        return
    if mode == "week":
        print("Codex Usage Governor — Governing Window")
        print(f"OBSERVED remaining: {status['remaining_percent']:.1f}%")
        print(f"OBSERVED reset: {fmt_time(status['window']['resets_at'])}")
        print(f"Window: {status['window']['window_minutes'] / 1440:g} days")
        print(f"PROJECTED sustainable rate: {status['sustainable_percent_per_day']:.1f}%/day")
        print(f"Status: {status['status']}")
        return
    print("Codex Usage Governor")
    print(f"OBSERVED remaining: {status['remaining_percent']:.1f}% (used {status['window']['used_percent']:.1f}%)")
    print(f"OBSERVED reset: {fmt_time(status['window']['resets_at'])} ({fmt_duration(status['remaining_seconds'])} remaining)")
    print(f"OBSERVED plan/model: {status['plan_type'] or 'unknown'} / {status['model'] or 'unknown'}")
    print(f"PROJECTED sustainable rate: {status['sustainable_percent_per_day']:.1f}%/day")
    print(f"OBSERVED used today: {status['used_today']:.1f}%")
    print(f"PROJECTED today's budget: {status['today_budget']:.1f}% ({status['today_remaining']:.1f}% remaining)")
    rate = status["burn_rate_percent_per_hour"]
    if rate is None:
        need = config["min_burn_data_hours"]
        print(f"ESTIMATED burn rate: gathering data ({status['burn_evidence_hours']:.2f}/{need:.2f}h)")
    else:
        print(f"ESTIMATED burn rate: {rate:.2f}%/hour ({status['burn_evidence_hours']:.2f}h evidence)")
        print(f"PROJECTED exhaustion: {fmt_time(status['projected_exhaustion'])}")
    print(f"Status: {status['status']}")


def print_history(rows: list[dict]) -> None:
    daily: dict[str, list[float]] = {}
    selected = latest_governing_window(rows)
    if not selected:
        print("No Codex usage readings collected yet."); return
    _, target = selected
    for row in rows:
        window = get_window(row, target["id"], target["lane"])
        if not window:
            continue
        day = dt.datetime.fromtimestamp(row["observed_at"]).astimezone().date().isoformat()
        daily.setdefault(day, []).append(float(window["used_percent"]))
    print("Locally observed daily usage")
    for day in sorted(daily):
        print(f"{day}: {max(daily[day]) - min(daily[day]):.1f}%")


def command_hook(args: argparse.Namespace, root: Path, history: Path) -> int:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        event = {}
    rows = collect(event.get("transcript_path"), args.sessions_dir, event.get("model"))
    append_rows(history, rows[-1:])
    print(json.dumps({"continue": True, "suppressOutput": True}))
    return 0


def command_work(args: argparse.Namespace, root: Path, history: Path, active_path: Path) -> int:
    rows = collect(None, args.sessions_dir, None)
    append_rows(history, rows)
    all_rows = read_history(history)
    selected = latest_governing_window(all_rows)
    if args.action == "start":
        if active_path.exists():
            print("A work block is already active. Stop it before starting another.", file=sys.stderr)
            return 2
        if not selected:
            print("No Codex allowance reading is available.", file=sys.stderr)
            return 2
        _, window = selected
        value = {
            "started_at": time.time(),
            "limit_id": window["id"],
            "lane": window["lane"],
            "resets_at": window["resets_at"],
            "starting_used_percent": window["used_percent"],
            "model": args.model,
            "reasoning": args.reasoning,
            "category": args.category,
            "note": args.note,
        }
        save_json(active_path, value)
        print(f"Work block started at {window['used_percent']:.1f}% used: {args.model} / {args.reasoning} / {args.category}")
        return 0
    if args.action == "stop":
        if not active_path.exists():
            print("No work block is active.", file=sys.stderr)
            return 2
        active = json.loads(active_path.read_text(encoding="utf-8"))
        ending = None
        for row in reversed(all_rows):
            ending = get_window(row, active["limit_id"], active["lane"], active["resets_at"])
            if ending:
                break
        if not ending:
            print("The allowance window reset during this work block; recording it without a consumption delta.")
        stopped_at = time.time()
        record = {
            **active,
            "stopped_at": stopped_at,
            "active_hours": (stopped_at - float(active["started_at"])) / 3600,
            "ending_used_percent": ending["used_percent"] if ending else None,
            "consumed_percent": max(0.0, ending["used_percent"] - float(active["starting_used_percent"])) if ending else None,
            "outcome": args.outcome,
            "time_saved_hours": args.time_saved_hours,
            "closing_note": args.note,
        }
        append_jsonl(root / "work-blocks.jsonl", record)
        active_path.unlink()
        consumed = "unknown" if record["consumed_percent"] is None else f"{record['consumed_percent']:.1f}%"
        print(f"Work block stopped: {consumed} consumed in {record['active_hours']:.2f}h; outcome={args.outcome}")
        return 0
    if not (root / "work-blocks.jsonl").exists():
        print("No completed work blocks yet.")
        return 0
    print((root / "work-blocks.jsonl").read_text(encoding="utf-8"), end="")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir")
    parser.add_argument("--sessions-dir")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init"); sub.add_parser("hook"); sub.add_parser("collect")
    report = sub.add_parser("report"); report.add_argument("mode", nargs="?", choices=["status", "bar", "compact", "today", "week", "history"], default="status")
    config_cmd = sub.add_parser("config"); config_cmd.add_argument("key", nargs="?"); config_cmd.add_argument("value", nargs="?")
    work = sub.add_parser("work")
    work.add_argument("action", choices=["start", "stop", "list"])
    work.add_argument("--model", default="unspecified")
    work.add_argument("--reasoning", default="unspecified")
    work.add_argument("--category", default="unspecified", choices=["planning", "implementation", "debugging", "research", "review", "media", "other", "unspecified"])
    work.add_argument("--outcome", default="unrated", choices=["accepted", "partial", "rework", "failed", "unrated"])
    work.add_argument("--time-saved-hours", type=float)
    work.add_argument("--note")
    args = parser.parse_args(argv)
    root, history_path, config_path, _ = data_paths(args.data_dir)
    ensure(root)
    if args.command == "init":
        load_config(root, config_path); history_path.touch(exist_ok=True); return 0
    if args.command == "hook":
        return command_hook(args, root, history_path)
    if args.command == "collect":
        collected = collect(None, args.sessions_dir, None)
        count = append_rows(history_path, collected)
        source = collected[-1]["source"] if collected else "none"
        print(f"Collected {count} new usage reading(s) from {source}."); return 0
    if args.command == "work":
        return command_work(args, root, history_path, root / "active-work.json")
    config = load_config(root, config_path)
    if args.command == "config":
        if args.key is None:
            for key, value in sorted(config.items()): print(f"{key} = {value}")
            return 0
        if args.key not in DEFAULT_CONFIG:
            print(f"Unknown config key: {args.key}", file=sys.stderr); return 2
        if args.value is None:
            print(f"{args.key} = {config[args.key]}"); return 0
        try: config[args.key] = float(args.value)
        except ValueError: print("Config values must be numeric.", file=sys.stderr); return 2
        save_json(config_path, config); print(f"{args.key} = {config[args.key]}"); return 0
    rows = read_history(history_path)
    if args.mode == "history": print_history(rows); return 0
    status = compute(rows, config)
    if status is None:
        print("No Codex rate-limit data collected yet. Run the collect command or complete a Codex turn with the plugin hook enabled.")
        return 0
    print_status(status, config, args.mode); return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
