import importlib.util
from pathlib import Path
import sys
import unittest


SCRIPTS = Path(__file__).parents[1] / "plugin" / "codex-usage-governor" / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("advisor", SCRIPTS / "advisor.py")
advisor = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(advisor)


class AdvisorTests(unittest.TestCase):
    def test_dnd_work_recommends_luna_without_shaming(self):
        choice = advisor.recommend(None, Path("D&D Campaign"), "plan a character", "fun draft", set())
        self.assertEqual("gpt-5.6-luna", choice["model"])
        self.assertIn("preserve your allowance", choice["why"])

    def test_high_stakes_work_keeps_sol_under_pressure(self):
        status = {"status": "RED", "remaining_percent": 10}
        choice = advisor.recommend(status, Path("app"), "production payment migration", "safe release", set())
        self.assertEqual("gpt-5.6-sol", choice["model"])
        self.assertEqual("high", choice["reasoning"])

    def test_missing_matching_plugin_gets_install_id(self):
        choice = advisor.recommend(None, Path("mobile-app"), "build a React interface", "polished UI", set())
        self.assertIn("ui-ux-pro-max@ui-ux-pro-max-skill", choice["install"])
        self.assertIn("browser@openai-bundled", choice["install"])

    def test_pressure_downgrade_explanation_matches_model(self):
        status = {"status": "RED", "remaining_percent": 70}
        choice = advisor.recommend(status, Path("utility"), "routine project task", "working draft", set())
        self.assertEqual("gpt-5.6-luna", choice["model"])
        self.assertIn("Luna", choice["why"])
        self.assertNotIn("Terra", choice["why"])


if __name__ == "__main__":
    unittest.main()
