"""שכבת תרגום קבצים → payloads עבור ClickUp.

viral-engine לא מדבר עם ClickUp ישירות — הסקריפט הזה רק ממיר את תוצרי הפייפליין
(01-stories.json, 02-ranking.json, script-NN.json) ל-payloads מוכנים; קריאות
ה-MCP עצמן (clickup_create_task, clickup_update_task וכו') מבוצעות ע"י קלוד
בסשן, לפי docs/CLICKUP-WORKFLOW.md.

שימוש:
    python pipeline/clickup_export.py <date>                     # תפריט → משימות
    python pipeline/clickup_export.py <date> --scripts            # תסריטים → עדכוני משימה
    python pipeline/clickup_export.py <date> --scripts --ids 4,19,3
"""
import argparse
import json
import re
import sys
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent.parent / "output"

MAX_NAME_LEN = 200

SCORE_LABELS = {
    "scroll_stop": "עצירת סקרול",
    "relevance": "רלוונטיות",
    "gate_potential": "פוטנציאל שער",
    "simplicity": "פשטות",
    "window": "חלון זמן",
    "fit": "התאמה",
}


def _score_bucket(score) -> str:
    """דלי ציון לתיוג: hot / warm / cold. ציון חסר → ללא דלי."""
    if not isinstance(score, (int, float)):
        return ""
    if score >= 80:
        return "hot"
    if score >= 65:
        return "warm"
    return "cold"


def _sources_md(sources: list) -> str:
    if not sources:
        return "_(אין מקורות)_"
    return "\n".join(f"- [{s}]({s})" for s in sources)


def _facts_md(facts: list) -> str:
    if not facts:
        return "_(אין עובדות מתועדות)_"
    return "\n".join(f"- {f}" for f in facts)


def _scores_line(scores: dict) -> str:
    if not scores:
        return ""
    parts = [f"{SCORE_LABELS.get(k, k)}: {v}" for k, v in scores.items()]
    return " · ".join(parts)


def build_task_payloads(stories: list, ranking: dict, date: str) -> list[dict]:
    """בונה payload למשימת ClickUp אחת לכל סיפור.

    סיפורים בלי רשומת דירוג (למשל אם הריצה נעצרה בין השלבים) עדיין נכנסים,
    עם ציון "—" ובלי תיוג דלי/recommended.
    """
    rk_by_id = {r["id"]: r for r in ranking.get("ranking", [])}
    recommended_ids = set(ranking.get("recommended_ids") or [])

    payloads = []
    for story in stories:
        sid = story["id"]
        rk = rk_by_id.get(sid, {})
        score = rk.get("total_score")
        is_recommended = sid in recommended_ids
        run_key = f"{date}#{sid}"

        name = (story.get("headline_he") or "").strip()[:MAX_NAME_LEN]

        lines = [
            f"## {story.get('headline_he', '')}",
            "",
            "### תקציר",
            story.get("story", "") or "_(אין תקציר)_",
            "",
            "### למה זה יעבוד",
            story.get("why_viral", "") or "_(לא צוין)_",
            "",
            f"### ציון: {score if score is not None else '—'}/100",
        ]
        scores_line = _scores_line(rk.get("scores", {}))
        if scores_line:
            lines.append(scores_line)
        lines.append("")

        outlier = story.get("source_outlier") or {}
        if outlier:
            lines += [
                f"🧬 פורמט מוכח: '{outlier.get('original_hook', '')}' "
                f"({outlier.get('page', '')}, {outlier.get('views', '')})",
                "",
            ]

        if rk.get("verdict"):
            lines += ["### שורה תחתונה", rk["verdict"], ""]
        if rk.get("angle"):
            lines += ["### הזווית המוצעת", rk["angle"], ""]
        if rk.get("suggested_gift"):
            lines += ["### מתנה מוצעת", rk["suggested_gift"], ""]

        lines += [
            "### טריות וכיסוי",
            f"**טריות:** {story.get('freshness', '') or '—'} | "
            f"**כיסוי בעברית:** {story.get('il_coverage', '') or '—'}",
            "",
            "### עובדות",
            _facts_md(story.get("facts", [])),
            "",
            "### מקורות",
            _sources_md(story.get("sources", [])),
            "",
            "---",
            f"`run_key: {run_key}`",
        ]
        markdown_description = "\n".join(lines)

        tags = ["viral-engine", f"menu:{date}"]
        if is_recommended:
            tags.append("recommended")
        bucket = _score_bucket(score)
        if bucket:
            tags.append(bucket)

        payloads.append({
            "name": name,
            "markdown_description": markdown_description,
            "tags": tags,
            "meta": {
                "run_key": run_key,
                "score": score,
                "recommended": is_recommended,
            },
        })

    return payloads


def _hook_families_md(hooks: list) -> list:
    """מרנדר את בלוק ההוקים. תומך גם בסכימה הישנה ({type, text}) וגם בחדשה
    ({family, options, loop})."""
    lines = ["### הוקים"]
    for h in hooks or []:
        if "text" in h:
            # תאימות לאחור — סכימה ישנה: {"type": "...", "text": "..."} —
            # הסימון "(מומלץ)" כבר מוטמע בתוך ה-type עצמו, כמו ב-render_gdoc_html.py
            lines.append(f"- **[{h.get('type', '')}]** {h.get('text', '')}")
            continue
        lines.append(f"**{h.get('family', '')}**")
        for j, opt in enumerate(h.get("options", [])):
            suffix = " ← מומלצת" if j == 0 else ""
            lines.append(f"- {opt}{suffix}")
        if h.get("loop"):
            lines.append(f"- לופ: {h['loop']}")
        lines.append("")
    return lines


def _script_table_md(beats: list) -> list:
    lines = [
        "### טבלת ביטים",
        "",
        "| זמן | ביט | טקסט | הגשה | ויז'ואל | מה מחזיק לביט הבא |",
        "|---|---|---|---|---|---|",
    ]
    for b in beats or []:
        lines.append(
            f"| {b.get('sec', '')} | {b.get('beat', '')} | {b.get('text', '')} | "
            f"{b.get('delivery', '')} | {b.get('visual', '')} | {b.get('retention', '')} |"
        )
    lines.append("")
    return lines


def build_script_update(script: dict, run_key: str) -> dict:
    """בונה עדכון משימה מתוך תסריט מוכן: תיאור מלא + תגובת סיכום קצרה."""
    gift = script.get("gift", {}) or {}

    lines = [
        f"## {script.get('title', '')}",
        "",
        f"**משך:** ~{script.get('duration_sec', '?')} שניות | "
        f"**מילת תגובה:** `{script.get('comment_word', '')}` | "
        f"**מתנה:** {gift.get('name', '')}",
        "",
    ]
    lines += _hook_families_md(script.get("hooks", []))
    lines += _script_table_md(script.get("script", []))

    lines += ["### הודעת DM", "", "> " + (script.get("dm_message", "") or "").replace("\n", "\n> "), ""]
    lines += [f"**המשך פאנל:** {script.get('funnel_next_step', '')}", ""]
    lines += ["### קפשן", "", "```", script.get("caption", "") or "", "```", ""]

    if script.get("onscreen_text"):
        lines += ["### טקסטים על המסך", ""] + [f"- {t}" for t in script["onscreen_text"]] + [""]

    if script.get("facts_to_verify"):
        lines += ["### עובדות לאימות לפני צילום", ""] + [f"- [ ] {f}" for f in script["facts_to_verify"]] + [""]

    notes = script.get("critic_notes", {}) or {}
    if notes:
        lines += ["### הערות המבקר", "", f"**ציון הוק:** {notes.get('hook_verdict', '')}", ""]
        lines += [f"- {c}" for c in notes.get("changes", [])]
        if notes.get("risk_flags"):
            lines += ["", "**🚩 דגלים:**"] + [f"- {r}" for r in notes["risk_flags"]]
        lines += [""]

    lines += ["---", f"`run_key: {run_key}`"]
    markdown_description = "\n".join(lines)

    hooks = script.get("hooks", []) or []
    if hooks:
        first = hooks[0]
        recommended_hook = first.get("text") or (first.get("options") or [""])[0]
    else:
        recommended_hook = ""

    comment_lines = [
        f"✅ תסריט מוכן — הוק מומלץ: {recommended_hook}",
        f"⏱ משך: ~{script.get('duration_sec', '?')} שניות",
        f"💬 מילת תגובה: {script.get('comment_word', '')}",
        f"🎁 מתנה: {gift.get('name', '')}",
        "התסריט המלא בתיאור המשימה ⬆",
    ]
    comment = "\n".join(comment_lines)

    return {"markdown_description": markdown_description, "comment": comment}


def _script_sort_key(p: Path):
    m = re.search(r"\d+", p.stem)
    return int(m.group()) if m else 0


def main():
    parser = argparse.ArgumentParser(description="מייצא payloads ל-ClickUp מתוצרי הפייפליין")
    parser.add_argument("date", help="תאריך הריצה, למשל 2026-07-04")
    parser.add_argument("--scripts", action="store_true", help="מייצא עדכוני תסריט במקום משימות תפריט")
    parser.add_argument("--ids", help="מיפוי run_key לתסריטים לפי סדר, למשל: 4,19,3")
    args = parser.parse_args()

    out_dir = OUTPUT / args.date
    if not out_dir.exists():
        print(f"❌  לא נמצאה תיקיית output עבור {args.date}", file=sys.stderr)
        return 1

    if args.scripts:
        script_paths = sorted(out_dir.glob("script-*.json"), key=_script_sort_key)
        if not script_paths:
            print(f"❌  לא נמצאו קובצי script-*.json ב-{out_dir}", file=sys.stderr)
            return 1

        ids = [x.strip() for x in args.ids.split(",")] if args.ids else None

        updates = []
        for i, path in enumerate(script_paths):
            script = json.loads(path.read_text(encoding="utf-8"))
            if ids and i < len(ids):
                run_key = f"{args.date}#{ids[i]}"
            else:
                run_key = f"{args.date}#{path.stem}"
            updates.append(build_script_update(script, run_key))

        out_path = out_dir / "clickup-script-updates.json"
        out_path.write_text(json.dumps(updates, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅  {len(updates)} עדכוני תסריט נכתבו ל-{out_path}")
        return 0

    stories_path = out_dir / "01-stories.json"
    ranking_path = out_dir / "02-ranking.json"
    if not stories_path.exists() or not ranking_path.exists():
        print(f"❌  חסרים 01-stories.json / 02-ranking.json ב-{out_dir}", file=sys.stderr)
        return 1

    stories = json.loads(stories_path.read_text(encoding="utf-8"))
    ranking = json.loads(ranking_path.read_text(encoding="utf-8"))

    payloads = build_task_payloads(stories, ranking, args.date)

    out_path = out_dir / "clickup-tasks.json"
    out_path.write_text(json.dumps(payloads, ensure_ascii=False, indent=2), encoding="utf-8")

    recommended_count = sum(1 for p in payloads if p["meta"]["recommended"])
    print(f"✅  {len(payloads)} משימות נכתבו ל-{out_path} ({recommended_count} מסומנות recommended)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
