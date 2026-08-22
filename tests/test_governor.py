import importlib.util
import json
from pathlib import Path
import unittest


SCRIPT = Path(__file__).parents[1] / "plugin" / "codex-usage-governor" / "scripts" / "governor.py"
SPEC = importlib.util.spec_from_file_location("governor", SCRIPT)
governor = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(governor)


class GovernorTests(unittest.TestCase):
    def setUp(self):
        self.sandbox = Path(__file__).parents[1] / ".test-data" / self._testMethodName
        self.sandbox.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        for path in sorted(self.sandbox.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        self.sandbox.rmdir()

    def test_normalizes_documented_app_server_response(self):
        result = {
            "rateLimitsByLimitId": {"codex": {
                "limitId": "codex", "planType": "plus",
                "primary": {"usedPercent": 1, "windowDurationMins": 10080, "resetsAt": 1893456000},
                "secondary": None, "credits": {"balance": "0"},
            }},
            "rateLimitResetCredits": {"availableCount": 0, "credits": []},
        }
        rows = governor.records_from_rate_limit_result(result, observed_at=100000)
        self.assertEqual(1, len(rows))
        self.assertEqual("codex-app-server", rows[0]["source"])
        self.assertEqual("plus", rows[0]["plan_type"])
        self.assertEqual(1.0, rows[0]["limits"][0]["used_percent"])
        self.assertEqual(0, rows[0]["reset_credits_available"])

    def record(self, observed, used, reset=700000.0, model="gpt-test"):
        return {
            "event_key": str(observed),
            "observed_at": observed,
            "source": "test",
            "session_id": "session",
            "model": model,
            "plan_type": "plus",
            "limits": [{
                "id": "codex", "lane": "primary", "used_percent": used,
                "window_minutes": 10080, "resets_at": reset,
            }],
            "tokens": None,
        }

    def test_normalizes_only_valid_windows(self):
        raw = {
            "limit_id": "codex",
            "primary": {"used_percent": 25, "window_minutes": 10080, "resets_at": 12345},
            "secondary": {"used_percent": 101, "window_minutes": 300, "resets_at": 12345},
        }
        windows = governor.normalize_limits(raw)
        self.assertEqual(1, len(windows))
        self.assertEqual("primary", windows[0]["lane"])

    def test_collects_structured_event_without_message_content(self):
        path = self.sandbox / "rollout.jsonl"
        events = [
                {"type": "session_meta", "payload": {"id": "abc"}},
                {"type": "turn_context", "payload": {"model": "gpt-5-test"}},
                {"type": "response_item", "payload": {"type": "message", "content": "SECRET"}},
                {"timestamp": "2026-01-01T00:00:00Z", "type": "event_msg", "payload": {
                    "type": "token_count",
                    "info": {"total_token_usage": {"total_tokens": 42}},
                    "rate_limits": {"limit_id": "codex", "plan_type": "plus", "primary": {
                        "used_percent": 12, "window_minutes": 10080, "resets_at": 1893456000
                    }},
                }},
        ]
        path.write_text("\n".join(json.dumps(event) for event in events), encoding="utf-8")
        rows = governor.collect_file(path)
        rendered = json.dumps(rows)
        self.assertEqual(1, len(rows))
        self.assertEqual("gpt-5-test", rows[0]["model"])
        self.assertNotIn("SECRET", rendered)

    def test_green_when_usage_is_under_daily_budget(self):
        rows = [self.record(100000, 10), self.record(136000, 11)]
        config = {**governor.DEFAULT_CONFIG, "min_burn_data_hours": 0.25}
        status = governor.compute(rows, config, now=136000)
        self.assertIsNotNone(status)
        self.assertEqual("GREEN", status["status"])

    def test_red_when_burn_rate_exhausts_before_reset(self):
        rows = [self.record(100000, 10, reset=200000), self.record(103600, 30, reset=200000)]
        config = {**governor.DEFAULT_CONFIG, "min_burn_data_hours": 0.25}
        status = governor.compute(rows, config, now=103600)
        self.assertEqual("RED", status["status"])
        self.assertLess(status["projected_exhaustion"], 200000)

    def test_history_append_is_idempotent(self):
        path = self.sandbox / "history.jsonl"
        row = self.record(100000, 10)
        self.assertEqual(1, governor.append_rows(path, [row]))
        self.assertEqual(0, governor.append_rows(path, [row]))
        self.assertEqual(1, len(governor.read_history(path)))


if __name__ == "__main__":
    unittest.main()
