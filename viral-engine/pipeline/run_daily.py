"""הריצה היומית — שני שלבים, עם בן כפילטר באמצע:

שלב 1 (מחקר):   python pipeline/run_daily.py
                → סקאוט + דירוג → תפריט בחירה (menu.md) עם כל הכותרות והציונים.
                שום דבר לא נפסל — בן בוחר.

שלב 2 (כתיבה):  python pipeline/run_daily.py --pick 3,10,5
                → תסריטים + ביקורת + בריף רק לסיפורים שנבחרו.

מצבים נוספים:
    --auto                 הכל בריצה אחת (הסוכן בוחר לפי ההמלצות) — למי שממהר
    --story "טקסט חופשי"   תסריט לסיפור שהבאת בעצמך, בלי סקאוט
"""
import argparse
import datetime
import json
import sys

from lib import OUTPUT, ask_claude, extract_json, load_config, load_prompt, load_style_guide, system_prompt


def scout(cfg, system):
    print("🔍  סוכן 1: סורק חדשות (עם חיפוש רשת)...")
    prompt = load_prompt(
        "01-news-scout.md",
        today=datetime.date.today().isoformat(),
        candidate_stories=cfg["daily"]["candidate_stories"],
        x_accounts=", ".join("@" + a for a in cfg["news"]["x_accounts"]),
        israeli_sources=", ".join(cfg["news"]["israeli_sources"]),
        topics="\n".join("- " + t for t in cfg["news"]["topics"]),
        creator_name=cfg["creator"]["name"],
        inspiration_pages="; ".join(
            f'{pg["handle"]} — {pg["url"]}' for pg in cfg["news"].get("inspiration_pages", [])
        ),
    )
    return extract_json(ask_claude(cfg, system, prompt, web_search=True, agent="scout"))


def score(cfg, system, stories):
    print(f"⚖️   סוכן 2: מדרג {len(stories)} סיפורים...")
    prompt = load_prompt(
        "02-virality-scorer.md",
        candidate_stories=len(stories),
        top_stories=cfg["daily"]["top_stories"],
        creator_name=cfg["creator"]["name"],
    )
    user = prompt + "\n\n## הסיפורים\n```json\n" + json.dumps(stories, ensure_ascii=False, indent=2) + "\n```"
    return extract_json(ask_claude(cfg, system, user, agent="scorer"))


def write_script(cfg, system, story, scorer_notes):
    prompt = load_prompt(
        "03-scriptwriter.md",
        creator_name=cfg["creator"]["name"],
        style_guide=load_style_guide("organic"),
        comment_triggers=", ".join(cfg["comment_triggers"]),
        lead_magnets="\n".join(f"- {m['name']}: {m['what']}" for m in cfg["lead_magnets"]),
    )
    user = (prompt
            + "\n\n## הסיפור\n```json\n" + json.dumps(story, ensure_ascii=False, indent=2) + "\n```"
            + "\n\n## הערות השופט\n```json\n" + json.dumps(scorer_notes, ensure_ascii=False, indent=2) + "\n```"
            + "\n\n## הפאנלים הזמינים\n```json\n" + json.dumps(cfg["funnels"], ensure_ascii=False, indent=2) + "\n```")
    return extract_json(ask_claude(cfg, system, user, agent="scriptwriter"))


def critique(cfg, system, script):
    prompt = load_prompt("05-critic.md", creator_name=cfg["creator"]["name"])
    user = prompt + "\n\n## התסריט לביקורת\n```json\n" + json.dumps(script, ensure_ascii=False, indent=2) + "\n```"
    return extract_json(ask_claude(cfg, system, user, agent="critic"))


def render_menu(stories, ranking, out_dir):
    """תפריט הבחירה של בן: כל הסיפורים + ציונים + המלצות. שום דבר לא נפסל."""
    by_id = {r["id"]: r for r in ranking.get("ranking", [])}
    order = [r["id"] for r in ranking.get("ranking", [])] or [s["id"] for s in stories]
    st_by_id = {s["id"]: s for s in stories}
    rec = set(ranking.get("recommended_ids") or ranking.get("selected_ids") or [])

    lines = [f"# תפריט סיפורים — {datetime.date.today().isoformat()}", "",
             "בחר את הסיפורים שמעניינים אותך והרץ: `python pipeline/run_daily.py --pick <מספרים>`", ""]
    for sid in order:
        st, rk = st_by_id.get(sid, {}), by_id.get(sid, {})
        star = " ⭐ מומלץ" if sid in rec else ""
        lines += [f"## {sid}. {st.get('headline_he','')}{star}",
                  f"**ציון:** {rk.get('total_score','—')}/100 | **טריות:** {st.get('freshness','')} | **כוסה בעברית:** {st.get('il_coverage','')}", "",
                  st.get("story",""), "",
                  f"**למה זה יעבוד:** {st.get('why_viral','')}"]
        if rk.get("verdict"):
            lines += [f"**שורה תחתונה:** {rk['verdict']}"]
        if rk.get("angle"):
            lines += [f"**הזווית המוצעת:** {rk['angle']} | **מתנה:** {rk.get('suggested_gift','')}"]
        lines += [""]
    (out_dir / "menu.md").write_text("\n".join(lines), encoding="utf-8")


def render_brief(scripts, ranking_info, out_dir):
    lines = [f"# בריף תוכן יומי — {datetime.date.today().isoformat()}", ""]
    for i, s in enumerate(scripts, 1):
        lines += [f"---\n\n## סרטון {i}: {s.get('title', '')}", ""]
        lines += [f"**משך:** ~{s.get('duration_sec', '?')} שניות | "
                  f"**מילת תגובה:** `{s.get('comment_word', '')}` | "
                  f"**מתנה:** {s.get('gift', {}).get('name', '')}", ""]
        lines += ["### הוקים (בחר אחד)"]
        for h in s.get("hooks", []):
            lines += [f"- **[{h.get('type','')}]** {h.get('text','')}"]
        lines += ["", "### התסריט", "", "| זמן | ביט | טקסט | הגשה | ויז'ואל |", "|---|---|---|---|---|"]
        for b in s.get("script", []):
            lines += [f"| {b.get('sec','')} | {b.get('beat','')} | {b.get('text','')} | {b.get('delivery','')} | {b.get('visual','')} |"]
        lines += ["", f"### הודעת DM (ManyChat)", "", "```", s.get("dm_message", ""), "```", ""]
        lines += [f"**המשך פאנל:** {s.get('funnel_next_step','')}", ""]
        lines += ["### קפשן", "", "```", s.get("caption", ""), "```", ""]
        if s.get("onscreen_text"):
            lines += ["### טקסטים על המסך", ""] + [f"- {t}" for t in s["onscreen_text"]] + [""]
        if s.get("facts_to_verify"):
            lines += ["### ⚠️ עובדות לאימות לפני צילום", ""] + [f"- [ ] {f}" for f in s["facts_to_verify"]] + [""]
        notes = s.get("critic_notes", {})
        if notes:
            lines += [f"### הערות המבקר", "", f"**ציון הוק:** {notes.get('hook_verdict','')}", ""]
            lines += [f"- {c}" for c in notes.get("changes", [])]
            if notes.get("risk_flags"):
                lines += ["", "**🚩 דגלים:**"] + [f"- {r}" for r in notes["risk_flags"]]
            lines += [""]
    (out_dir / "brief.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--story", help="דלג על הסקאוט וכתוב תסריט לסיפור שתספק ידנית")
    parser.add_argument("--pick", help="שלב 2: מספרי הסיפורים שבחרת, מופרדים בפסיק (למשל: 3,10,5)")
    parser.add_argument("--auto", action="store_true", help="ריצה מלאה בלי עצירה — הסוכן בוחר לפי ההמלצות")
    args = parser.parse_args()

    cfg = load_config()
    system = system_prompt(cfg)
    out_dir = OUTPUT / datetime.date.today().isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---- מצב סיפור ידני ----
    if args.story:
        stories = [{"id": 1, "headline_he": "סיפור ידני", "story": args.story,
                    "why_viral": "", "facts": [], "sources": [], "evergreen": True}]
        selected = [{"id": 1, "angle": "", "suggested_gift": "", "notes": ""}]
        return write_and_brief(cfg, system, stories, selected, out_dir)

    # ---- שלב 2: בן בחר ----
    if args.pick:
        stories = json.loads((out_dir / "01-stories.json").read_text(encoding="utf-8"))
        ranking = json.loads((out_dir / "02-ranking.json").read_text(encoding="utf-8"))
        picked = [int(x) for x in args.pick.replace(" ", "").split(",")]
        by_id = {s["id"]: s for s in stories}
        rk_by_id = {r["id"]: r for r in ranking.get("ranking", [])}
        sel_stories = [by_id[i] for i in picked]
        selected = [rk_by_id.get(i, {"id": i, "angle": "", "suggested_gift": "", "notes": ""}) for i in picked]
        return write_and_brief(cfg, system, sel_stories, selected, out_dir)

    # ---- שלב 1: מחקר + תפריט ----
    stories = scout(cfg, system)
    (out_dir / "01-stories.json").write_text(json.dumps(stories, ensure_ascii=False, indent=2), encoding="utf-8")
    ranking = score(cfg, system, stories)
    (out_dir / "02-ranking.json").write_text(json.dumps(ranking, ensure_ascii=False, indent=2), encoding="utf-8")
    render_menu(stories, ranking, out_dir)
    print(f"\n📋  התפריט מוכן: {out_dir / 'menu.md'}")

    if args.auto:
        picked = ranking.get("recommended_ids") or ranking.get("selected_ids") or []
        by_id = {s["id"]: s for s in stories}
        rk_by_id = {r["id"]: r for r in ranking.get("ranking", [])}
        return write_and_brief(cfg, system, [by_id[i] for i in picked],
                               [rk_by_id[i] for i in picked], out_dir)

    print("👉  עכשיו תורך: בחר מספרים והרץ  python pipeline/run_daily.py --pick 3,10,5")


def write_and_brief(cfg, system, stories, selected, out_dir):
    final_scripts = []
    for i, (story, notes) in enumerate(zip(stories, selected), 1):
        print(f"✍️   סוכן 3: כותב תסריט {i}/{len(stories)}: {story.get('headline_he','')[:60]}")
        draft = write_script(cfg, system, story, notes)
        print(f"🧐  סוכן 4: ביקורת ושיפור תסריט {i}...")
        final = critique(cfg, system, draft)
        final_scripts.append(final)
        (out_dir / f"script-{i}.json").write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")

    render_brief(final_scripts, selected, out_dir)
    print(f"\n✅  מוכן! הבריף המלא: {out_dir / 'brief.md'}")


if __name__ == "__main__":
    sys.exit(main())
