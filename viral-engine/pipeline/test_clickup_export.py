"""בדיקות ל-clickup_export.py — מריץ על נתוני אמת (output/2026-07-04) ועל
פיקסצ'רים לתסריטים בסכימה החדשה והישנה.

הרצה:  python pipeline/test_clickup_export.py
"""
import json
import unittest
from pathlib import Path

from clickup_export import build_script_update, build_task_payloads

ROOT = Path(__file__).resolve().parent.parent
REAL_DATE = "2026-07-04"
REAL_DIR = ROOT / "output" / REAL_DATE


NEW_SCHEMA_SCRIPT = {
    "title": "הילד שמכר אפליקציית צילום-אוכל בתשעה ספרות",
    "duration_sec": 50,
    "hooks": [
        {
            "family": "מספר מטורף",
            "options": [
                "ילד בן 17 בנה אפליקציה בחדר שלו — ומכר אותה בתשעה ספרות.",
                "בזמן שהחברים שלו למדו לבגרויות, הוא מכר חברה בתשעה ספרות.",
            ],
            "loop": "האקזיט השני שלו — הראשון היה בגיל 16",
        },
        {
            "family": "דמות לא צפויה",
            "options": ["האפליקציה הזאת עושה דבר אחד — מצלמת אוכל."],
        },
    ],
    "script": [
        {
            "beat": "hook",
            "sec": "0-4",
            "text": "ילד בן 17 בנה אפליקציה בחדר שלו.",
            "delivery": "מהיר, ישר לעניין",
            "visual": "תמונה + כתובית '17'",
            "retention": "מספר + גיל בשנייה הראשונה",
        },
        {
            "beat": "cta",
            "sec": "43-52",
            "text": "תגיבו \"אפליקציה\".",
            "delivery": "אנרגיה חוזרת",
            "visual": "כתובית ענקית",
            "retention": "שער תגובות",
        },
    ],
    "comment_word": "אפליקציה",
    "gift": {"name": "מדריך בניית אפליקציה ראשונה עם AI", "what": "PDF צעד-אחר-צעד"},
    "dm_message": "הנה המדריך שהבטחתי 🎁\nולינק לוובינר",
    "funnel_next_step": "וובינר Base44",
    "caption": "הוא בן 17. מה התירוץ שלנו?",
    "onscreen_text": ["בן 17. אקזיט של 9 ספרות.", "$40,000,000 בשנה"],
    "facts_to_verify": ["סכום העסקה המדויק לא פורסם"],
    "critic_notes": {
        "changes": ["קוצר ההוק מ-16 ל-12 מילים"],
        "hook_verdict": "9/10",
        "risk_flags": ["אין לציין סכום עסקה מדויק"],
    },
}

OLD_SCHEMA_SCRIPT = json.loads((ROOT / "output" / "2026-07-02" / "script-1.json").read_text(encoding="utf-8"))


class TestBuildTaskPayloads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stories = json.loads((REAL_DIR / "01-stories.json").read_text(encoding="utf-8"))
        cls.ranking = json.loads((REAL_DIR / "02-ranking.json").read_text(encoding="utf-8"))
        cls.payloads = build_task_payloads(cls.stories, cls.ranking, REAL_DATE)
        cls.by_run_key = {p["meta"]["run_key"]: p for p in cls.payloads}

    def test_count(self):
        self.assertEqual(len(self.payloads), 21)

    def test_recommended_story_has_correct_score_and_flag(self):
        key = f"{REAL_DATE}#4"
        self.assertIn(key, self.by_run_key)
        payload = self.by_run_key[key]
        self.assertEqual(payload["meta"]["score"], 85)
        self.assertTrue(payload["meta"]["recommended"])
        self.assertIn("recommended", payload["tags"])
        self.assertIn("hot", payload["tags"])
        self.assertIn(f"menu:{REAL_DATE}", payload["tags"])
        self.assertIn("viral-engine", payload["tags"])
        self.assertIn(f"run_key: {key}", payload["markdown_description"])

    def test_non_recommended_story_not_flagged(self):
        key = f"{REAL_DATE}#1"
        payload = self.by_run_key[key]
        self.assertFalse(payload["meta"]["recommended"])
        self.assertNotIn("recommended", payload["tags"])

    def test_sources_rendered_as_markdown_links(self):
        key = f"{REAL_DATE}#4"
        payload = self.by_run_key[key]
        story = next(s for s in self.stories if s["id"] == 4)
        for url in story["sources"]:
            self.assertIn(f"[{url}]({url})", payload["markdown_description"])

    def test_name_truncated_to_200_chars(self):
        for p in self.payloads:
            self.assertLessEqual(len(p["name"]), 200)

    def test_story_without_ranking_still_included(self):
        # מדמה סיפור בלי דירוג — לא אמור לקרוס, ציון "—", לא recommended
        stories = self.stories + [{
            "id": 999, "headline_he": "סיפור בלי דירוג", "story": "טקסט",
            "why_viral": "", "facts": [], "sources": [], "evergreen": True,
            "freshness": "", "il_coverage": "",
        }]
        payloads = build_task_payloads(stories, self.ranking, REAL_DATE)
        payload = next(p for p in payloads if p["meta"]["run_key"] == f"{REAL_DATE}#999")
        self.assertIsNone(payload["meta"]["score"])
        self.assertFalse(payload["meta"]["recommended"])
        self.assertIn("—/100", payload["markdown_description"])


class TestBuildScriptUpdate(unittest.TestCase):
    def test_new_schema(self):
        update = build_script_update(NEW_SCHEMA_SCRIPT, "2026-07-04#4")
        md = update["markdown_description"]
        self.assertIn("הילד שמכר אפליקציית צילום-אוכל בתשעה ספרות", md)
        self.assertIn("מספר מטורף", md)
        self.assertIn("← מומלצת", md)
        self.assertIn("האקזיט השני שלו", md)  # loop
        self.assertIn("| 0-4 | hook |", md)
        self.assertIn("מספר + גיל בשנייה הראשונה", md)  # retention column
        self.assertIn("- [ ] סכום העסקה המדויק לא פורסם", md)
        self.assertIn("9/10", md)
        self.assertIn("🚩 דגלים", md)
        self.assertIn("run_key: 2026-07-04#4", md)

        comment = update["comment"]
        self.assertIn("אפליקציה", comment)
        self.assertIn("התסריט המלא בתיאור המשימה", comment)
        self.assertIn("ילד בן 17 בנה אפליקציה בחדר שלו — ומכר אותה בתשעה ספרות.", comment)

    def test_old_schema_backward_compat(self):
        update = build_script_update(OLD_SCHEMA_SCRIPT, "2026-07-02#script-1")
        md = update["markdown_description"]
        self.assertIn("הילד שמכר אפליקציית צילום-אוכל בתשעה ספרות", md)
        self.assertIn("מספר מטורף (מומלץ)", md)
        self.assertIn("ילד בן 17 בנה אפליקציה בחדר שלו — ומכר אותה בתשעה ספרות לפני הקולג'.", md)
        self.assertIn("| 0-4 | hook |", md)
        self.assertIn("run_key: 2026-07-02#script-1", md)

        comment = update["comment"]
        self.assertIn("אפליקציה", comment)
        self.assertIn("ילד בן 17 בנה אפליקציה בחדר שלו", comment)


if __name__ == "__main__":
    unittest.main(verbosity=2)
