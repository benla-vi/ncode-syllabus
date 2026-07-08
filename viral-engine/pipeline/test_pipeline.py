"""בדיקות עצמאיות (בלי קריאה לרשת/לקלוד) ל-lib.load_prompt, render_brief,
render_gdoc_html.render/render_menu, ו-run_daily.resolve_run_dir / render_menu.

הרצה:  python pipeline/test_pipeline.py
"""
import json
import sys
import tempfile
from pathlib import Path

import lib
import render_gdoc_html
import run_daily

FAILURES = []


def check(name, condition, detail=""):
    status = "✅ PASS" if condition else "❌ FAIL"
    print(f"{status}  {name}" + (f"  — {detail}" if detail and not condition else ""))
    if not condition:
        FAILURES.append(name)


# ---------------------------------------------------------------------------
# 1. load_prompt על כל 7 הפרומפטים
# ---------------------------------------------------------------------------

def test_load_prompt_all():
    common = dict(
        creator_name="בן לביא",
        creator_handle="@benlavi",
        niche="AI ובניית אפליקציות",
        audience="ביזאופרים",
        tone="אנרגטי",
        today="2026-07-07",
        candidate_stories=21,
        top_stories=3,
        x_accounts="@rowancheung, @sama",
        israeli_sources="Geektime",
        topics="- נושא 1\n- נושא 2",
        inspiration_pages="@wealth — https://instagram.com/wealth",
        style_guide="(מדריך סגנון לדוגמה)",
        comment_triggers="AI, כלים",
        lead_magnets="- חבילת פרומפטים: 50 פרומפטים",
        num_ads=5,
        ads_style_guide="(מדריך מכירה לדוגמה)",
        audience_context="[קהל]",
        brand_context="[מותג]",
        research_channels="- @wealth (אינסטגרם): סיפורי כסף",
    )

    files_and_markers = {
        "00-system-core.md": [],
        "01-news-scout.md": ['"headline_he"', '"il_coverage"', '"source_outlier"'],
        "02-virality-scorer.md": ['"total_score"', '"recommended_ids"'],
        "03-scriptwriter.md": ['"hooks"', '"retention"', '"loop_close"'],
        "04-ad-writer.md": ['"ads"', '"policy_notes"'],
        "05-critic.md": ['"critic_notes"', '"risk_flags"'],
        "06-style-modeler.md": [],
    }

    for name, markers in files_and_markers.items():
        try:
            out = lib.load_prompt(name, **common)
            ok = True
        except Exception as e:  # noqa
            out = ""
            ok = False
            check(f"load_prompt({name}) לא קורס", False, str(e))
            continue
        check(f"load_prompt({name}) לא קורס", ok)
        check(f"load_prompt({name}): אין placeholder שלא הוחלף", "${" not in out)
        check(f"load_prompt({name}): אין ${{audience_context}} שיורי", "${audience_context}" not in out)
        check(f"load_prompt({name}): אין ${{brand_context}} שיורי", "${brand_context}" not in out)
        raw_source = (lib.PROMPTS / name).read_text(encoding="utf-8")
        if "creator_name" in raw_source:
            check(f"load_prompt({name}): ${{creator_name}} הוחלף", "בן לביא" in out)
        if "audience_context" in raw_source:
            check(f"load_prompt({name}): ${{audience_context}} הוחלף", "[קהל]" in out)
        if "brand_context" in raw_source:
            check(f"load_prompt({name}): ${{brand_context}} הוחלף", "[מותג]" in out)
        for m in markers:
            check(f"load_prompt({name}): בלוק JSON לדוגמה נשאר שלם ({m})", m in out, f"'{m}' לא נמצא בפלט")

    # הסקאוט מכיל "made $" בדוגמה — ולידציה שזה לא קורס את ה-Template
    scout_out = lib.load_prompt("01-news-scout.md", **common)
    check('פרומפט הסקאוט עם "made $" לא קורס', 'made $' in scout_out)
    check("פרומפט הסקאוט: אין ${research_channels} שיורי", "${research_channels}" not in scout_out)
    check("פרומפט הסקאוט: סעיף שכבת האאוטליירים קיים", "שכבת אאוטליירים" in scout_out)


# ---------------------------------------------------------------------------
# פיקסצ'רים
# ---------------------------------------------------------------------------

def make_new_schema_script():
    return {
        "title": "סרטון בדיקה",
        "duration_sec": 45,
        "hooks": [
            {"family": "תבנית הלופ", "options": ["אופציה A", "אופציה B", "אופציה C"], "loop": "מה שיקרה בסוף"},
            {"family": "איום ישיר", "options": ["אופציה D", "אופציה E"], "loop": ""},
        ],
        "script": [
            {"beat": "hook", "sec": "0-4", "text": "הוק", "delivery": "מהיר", "visual": "טקסט", "retention": "לופ נפתח"},
            {"beat": "tension", "sec": "3-10", "text": "מתח", "delivery": "...", "visual": "...", "retention": "מעלה הימור"},
            {"beat": "story", "sec": "10-30", "text": "הסיפור", "delivery": "...", "visual": "...", "retention": "טוויסט"},
            {"beat": "value", "sec": "30-40", "text": "הערך", "delivery": "...", "visual": "...", "retention": "רלוונטיות"},
            {"beat": "loop_close", "sec": "38-45", "text": "ועכשיו מה שהבטחתי לכם: הנה זה", "delivery": "...", "visual": "...", "retention": "הפאיוף — הסיבה שנשארו"},
            {"beat": "cta", "sec": "40-50", "text": "תגיבו במילה", "delivery": "...", "visual": "...", "retention": "הצעה"},
        ],
        "comment_word": "AI",
        "gift": {"name": "מדריך", "what": "PDF"},
        "dm_message": "הנה המדריך",
        "funnel_next_step": "יוטיוב",
        "caption": "קפשן",
        "onscreen_text": ["טקסט 1"],
        "facts_to_verify": ["עובדה 1"],
        "critic_notes": {"changes": ["שינוי 1"], "hook_verdict": "9/10", "risk_flags": []},
    }


def make_old_schema_script():
    return {
        "title": "סרטון ישן",
        "duration_sec": 40,
        "hooks": [
            {"type": "מספר מטורף (מומלץ)", "text": "הוק ישן 1"},
            {"type": "דמות לא צפויה", "text": "הוק ישן 2"},
        ],
        "script": [
            {"beat": "hook", "sec": "0-4", "text": "טקסט", "delivery": "...", "visual": "..."},
            {"beat": "cta", "sec": "40-50", "text": "CTA", "delivery": "...", "visual": "..."},
        ],
        "comment_word": "כלים",
        "gift": {"name": "רשימה", "what": "כלים"},
        "dm_message": "הנה",
        "funnel_next_step": "קורס",
        "caption": "קפשן ישן",
    }


# ---------------------------------------------------------------------------
# 2. פיקסצ'ר תסריט בסכימה החדשה: render_brief + render_gdoc_html.render
# ---------------------------------------------------------------------------

def test_new_schema_rendering():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_out = Path(tmp)
        day = tmp_out / "2026-07-10"
        day.mkdir(parents=True)
        script = make_new_schema_script()
        (day / "script-01.json").write_text(json.dumps(script, ensure_ascii=False), encoding="utf-8")

        # run_daily.render_brief
        run_daily.render_brief([script], day)
        brief_md = (day / "brief.md").read_text(encoding="utf-8")
        check("render_brief (md): כל אופציות ההוק מופיעות", all(o in brief_md for o in ["אופציה A", "אופציה B", "אופציה C", "אופציה D", "אופציה E"]))
        check("render_brief (md): מומלץ מסומן לאופציה הראשונה", "אופציה A ← מומלץ" in brief_md)
        check("render_brief (md): הלופ מופיע", "מה שיקרה בסוף" in brief_md)
        check("render_brief (md): עמודת retention בטבלה", "מה מחזיק לביט הבא" in brief_md and "הפאיוף — הסיבה שנשארו" in brief_md)
        check("render_brief (md): ביט loop_close מופיע", "loop_close" in brief_md and "ועכשיו מה שהבטחתי לכם" in brief_md)
        check("render_brief (md): אין 'נפסלו' בפלט", "נפסלו" not in brief_md and "נפסל" not in brief_md)

        # render_gdoc_html.render — מצביע על ה-OUTPUT הזמני
        orig_output = render_gdoc_html.OUTPUT
        render_gdoc_html.OUTPUT = tmp_out
        try:
            out_path = render_gdoc_html.render("2026-07-10")
            html_out = out_path.read_text(encoding="utf-8")
        finally:
            render_gdoc_html.OUTPUT = orig_output

        # פורמט טלפרומפטר רזה: מוצג רק ההוק המומלץ (אופציה A), בלי האלטרנטיבות, בלי טבלה
        check("render_gdoc_html.render (html): ההוק המומלץ מוצג", "אופציה A" in html_out)
        check("render_gdoc_html.render (html): אלטרנטיבות ההוק לא מעמיסות", "אופציה E" not in html_out)
        check("render_gdoc_html.render (html): כותרת ההוק מופיעה", "▶ ההוק" in html_out)
        check("render_gdoc_html.render (html): סימון סגירת הלופ", "🔓" in html_out)
        check("render_gdoc_html.render (html): טלפרומפטר אנכי (לא טבלה)", "📝 התסריט" in html_out and "<table" not in html_out)
        check("render_gdoc_html.render (html): ביט loop_close מופיע", "ועכשיו מה שהבטחתי לכם" in html_out)
        check("render_gdoc_html.render (html): אין 'נפסלו' בפלט", "נפסלו" not in html_out and "רejected_summary" not in html_out)


# ---------------------------------------------------------------------------
# 3. תאימות לאחור — סכימה ישנה
# ---------------------------------------------------------------------------

def test_old_schema_backcompat():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_out = Path(tmp)
        day = tmp_out / "2026-07-11"
        day.mkdir(parents=True)
        script = make_old_schema_script()
        (day / "script-01.json").write_text(json.dumps(script, ensure_ascii=False), encoding="utf-8")

        run_daily.render_brief([script], day)
        brief_md = (day / "brief.md").read_text(encoding="utf-8")
        check("תאימות לאחור (md): הוק ישן מרונדר עם [type] text", "[מספר מטורף (מומלץ)]" in brief_md and "הוק ישן 1" in brief_md)

        orig_output = render_gdoc_html.OUTPUT
        render_gdoc_html.OUTPUT = tmp_out
        try:
            out_path = render_gdoc_html.render("2026-07-11")
            html_out = out_path.read_text(encoding="utf-8")
        finally:
            render_gdoc_html.OUTPUT = orig_output
        check("תאימות לאחור (html): הוק ישן מרונדר בקופסת ההוק", "הוק ישן 1" in html_out)


# ---------------------------------------------------------------------------
# 4. resolve_run_dir
# ---------------------------------------------------------------------------

def test_resolve_run_dir():
    explicit = run_daily.resolve_run_dir("2026-01-01")
    check("resolve_run_dir עם תאריך מפורש", explicit == lib.OUTPUT / "2026-01-01")

    auto = run_daily.resolve_run_dir(None)
    check("resolve_run_dir בלי תאריך בוחר תיקייה מתוארכת עם 01-stories.json",
          (auto / "01-stories.json").exists(), str(auto))

    missing = run_daily.resolve_run_dir("2099-12-31")
    check("resolve_run_dir עם תאריך לא קיים לא קורס ומחזיר נתיב", missing == lib.OUTPUT / "2099-12-31")


# ---------------------------------------------------------------------------
# 5. מיון נומרי של script-*.json
# ---------------------------------------------------------------------------

def test_numeric_script_sort():
    paths = [Path(f"script-{n}.json") for n in [1, 10, 11, 12, 2, 3, 4, 5, 6, 7, 8, 9]]
    ordered = sorted(paths, key=render_gdoc_html._script_sort_key)
    expected = [f"script-{n}.json" for n in range(1, 13)]
    check("מיון נומרי של 12 קבצי script-*.json", [p.name for p in ordered] == expected,
          str([p.name for p in ordered]))


# ---------------------------------------------------------------------------
# 6. render_menu כולל סיפור שלא מופיע ב-ranking
# ---------------------------------------------------------------------------

def test_render_menu_includes_unranked_story():
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp)
        stories = [
            {"id": 1, "headline_he": "סיפור מדורג", "story": "...", "why_viral": "...", "freshness": "", "il_coverage": ""},
            {"id": 2, "headline_he": "סיפור בלי דירוג", "story": "...", "why_viral": "...", "freshness": "", "il_coverage": ""},
        ]
        ranking = {"ranking": [{"id": 1, "total_score": 90}], "recommended_ids": [1]}
        run_daily.render_menu(stories, ranking, out_dir)
        menu_md = (out_dir / "menu.md").read_text(encoding="utf-8")
        check("render_menu כולל סיפור שלא ב-ranking", "סיפור בלי דירוג" in menu_md)


def test_loop_tower_in_scriptwriter():
    out = lib.load_prompt(
        "03-scriptwriter.md",
        creator_name="בן לביא", style_guide="(מדריך)", comment_triggers="AI",
        lead_magnets="- מתנה", audience_context="[קהל]", brand_context="[מותג]",
    )
    check("פרומפט 03: סעיף מגדל לופים קיים", "מגדל לופים" in out)
    check("פרומפט 03: פורמט retention החדש (לופים פתוחים:)", "לופים פתוחים:" in out)
    check("פרומפט 03: כלל הברזל", "אף פעם לא סוגרים לופ בלי שלופ אחר כבר פתוח" in out)


def main():
    test_load_prompt_all()
    test_loop_tower_in_scriptwriter()
    test_new_schema_rendering()
    test_old_schema_backcompat()
    test_resolve_run_dir()
    test_numeric_script_sort()
    test_render_menu_includes_unranked_story()

    print()
    if FAILURES:
        print(f"❌ {len(FAILURES)} בדיקות נכשלו:")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    print("✅ כל הבדיקות עברו.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
