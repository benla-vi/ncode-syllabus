"""ממיר את תוצרי ריצה יומית ל-HTML מעוצב (RTL) שמוכן להמרה לגוגל דוקס.

שימוש:  python pipeline/render_gdoc_html.py [YYYY-MM-DD]   (ברירת מחדל: היום)
פלט:    output/<date>/brief.html
"""
import datetime
import html
import json
import re
import sys
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent.parent / "output"


# אימוג'ים מחוץ ל-BMP נשברים בהמרת HTML→Docs — מחליפים בסמלים בטוחים
SAFE = {"👇": "⬇", "🎁": "✦", "🤯": "‼", "🚩": "⚑", "🎬": "▶", "👀": "◉", "🔍": "⌕"}

def esc(s):
    t = str(s or "")
    for k, v in SAFE.items():
        t = t.replace(k, v)
    # כל תו שנשאר מחוץ ל-BMP מוחלף כדי לא להישבר בהמרה
    t = "".join(c if ord(c) < 0x10000 else "•" for c in t)
    return html.escape(t)


def _script_sort_key(p: Path):
    m = re.search(r"\d+", p.stem)
    return int(m.group()) if m else 0


def render(date_str: str) -> Path:
    day = OUTPUT / date_str
    scripts = [json.loads(p.read_text(encoding="utf-8"))
               for p in sorted(day.glob("script-*.json"), key=_script_sort_key)]
    ranking = {}
    rp = day / "02-ranking.json"
    if rp.exists():
        ranking = json.loads(rp.read_text(encoding="utf-8"))

    h = [f'<div dir="rtl"><h1>▶ בריף תוכן יומי — {esc(date_str)}</h1>']

    for i, s in enumerate(scripts, 1):
        h.append(f'<h1>סרטון {i}: {esc(s.get("title"))}</h1>')
        h.append(f'<p><b>משך:</b> ~{esc(s.get("duration_sec","?"))} שניות &nbsp;|&nbsp; '
                 f'<b>מילת תגובה:</b> {esc(s.get("comment_word"))} &nbsp;|&nbsp; '
                 f'<b>מתנה:</b> {esc(s.get("gift",{}).get("name"))}</p>')

        h.append("<h2>הוקים (בחר אחד)</h2>")
        for hk in s.get("hooks", []):
            if "text" in hk:
                # תאימות לאחור — סכימה ישנה: {"type": "...", "text": "..."}
                h.append(f'<p><b>[{esc(hk.get("type"))}]</b> {esc(hk.get("text"))}</p>')
                continue
            h.append(f'<p><b>{esc(hk.get("family"))}</b></p><ul>')
            options = hk.get("options", [])
            for j, opt in enumerate(options):
                suffix = " — ← מומלץ" if j == 0 else ""
                h.append(f'<li>{esc(opt)}{suffix}</li>')
            h.append("</ul>")
            if hk.get("loop"):
                h.append(f'<p><b>לופ:</b> {esc(hk["loop"])}</p>')

        h.append("<h2>התסריט</h2>")
        h.append('<table border="1" cellpadding="6" style="border-collapse:collapse">'
                 "<tr><th>זמן</th><th>ביט</th><th>מה אומרים</th><th>איך מגישים</th><th>מה על המסך</th>"
                 "<th>מה מחזיק לביט הבא</th></tr>")
        for b in s.get("script", []):
            h.append(f'<tr><td>{esc(b.get("sec"))}</td><td>{esc(b.get("beat"))}</td>'
                     f'<td>{esc(b.get("text"))}</td><td>{esc(b.get("delivery"))}</td>'
                     f'<td>{esc(b.get("visual"))}</td><td>{esc(b.get("retention",""))}</td></tr>')
        h.append("</table>")

        h.append("<h2>הודעת DM (ManyChat)</h2>")
        h.append(f'<p style="background:#f2f2f2;padding:8px">{esc(s.get("dm_message")).replace(chr(10), "<br>")}</p>')
        h.append(f'<p><b>המשך פאנל:</b> {esc(s.get("funnel_next_step"))}</p>')

        h.append("<h2>קפשן</h2>")
        h.append(f'<p style="background:#f2f2f2;padding:8px">{esc(s.get("caption")).replace(chr(10), "<br>")}</p>')

        if s.get("onscreen_text"):
            h.append("<h2>טקסטים על המסך</h2><ul>")
            h += [f"<li>{esc(t)}</li>" for t in s["onscreen_text"]]
            h.append("</ul>")

        if s.get("facts_to_verify"):
            h.append("<h2>⚠️ עובדות לאימות לפני צילום</h2><ul>")
            h += [f"<li>☐ {esc(f)}</li>" for f in s["facts_to_verify"]]
            h.append("</ul>")

        notes = s.get("critic_notes") or {}
        if notes:
            h.append("<h2>הערות המבקר</h2>")
            h.append(f'<p><b>ציון הוק:</b> {esc(notes.get("hook_verdict"))}</p><ul>')
            h += [f"<li>{esc(c)}</li>" for c in notes.get("changes", [])]
            h.append("</ul>")
            if notes.get("risk_flags"):
                h.append("<p><b>⚑ דגלים:</b></p><ul>")
                h += [f"<li>{esc(r)}</li>" for r in notes["risk_flags"]]
                h.append("</ul>")
        h.append("<hr>")

    h.append("</div>")
    out = day / "brief.html"
    out.write_text("\n".join(h), encoding="utf-8")
    return out


def render_menu(date_str: str) -> Path:
    """תפריט בחירת הסיפורים כ-HTML מוכן לגוגל דוקס."""
    day = OUTPUT / date_str
    stories = json.loads((day / "01-stories.json").read_text(encoding="utf-8"))
    ranking = {}
    rp = day / "02-ranking.json"
    if rp.exists():
        ranking = json.loads(rp.read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in ranking.get("ranking", [])}
    order = [r["id"] for r in ranking.get("ranking", [])] or [st["id"] for st in stories]
    order += [st["id"] for st in stories if st["id"] not in order]
    st_by_id = {st["id"]: st for st in stories}
    rec = set(ranking.get("recommended_ids") or ranking.get("selected_ids") or [])

    h = [f'<div dir="rtl"><h1>◈ תפריט סיפורים — {esc(date_str)}</h1>',
         '<p><b>איך זה עובד:</b> אלה כל הסיפורים שהמחקר של היום מצא, ממוינים לפי ציון. '
         'שום דבר לא נפסל — ⭐ זו רק המלצת המערכת. סמן/כתוב לי אילו מספרים אתה בוחר '
         '(למשל: "3, 10, 5") ורק הם יהפכו לתסריטים מלאים.</p>']
    for sid in order:
        st, rk = st_by_id.get(sid, {}), by_id.get(sid, {})
        star = " ⭐" if sid in rec else ""
        h.append(f'<h2>{sid}. {esc(st.get("headline_he"))}{star}</h2>')
        h.append(f'<p><b>ציון:</b> {esc(rk.get("total_score","—"))}/100 &nbsp;|&nbsp; '
                 f'<b>טריות:</b> {esc(st.get("freshness"))} &nbsp;|&nbsp; '
                 f'<b>כוסה בעברית:</b> {esc(st.get("il_coverage"))}</p>')
        h.append(f'<p>{esc(st.get("story"))}</p>')
        h.append(f'<p><b>למה זה יעבוד:</b> {esc(st.get("why_viral"))}</p>')
        if rk.get("verdict"):
            h.append(f'<p><b>שורה תחתונה:</b> {esc(rk.get("verdict"))}</p>')
        if rk.get("angle"):
            h.append(f'<p><b>הזווית המוצעת:</b> {esc(rk.get("angle"))}<br><b>מתנה מוצעת:</b> {esc(rk.get("suggested_gift"))}</p>')
    h.append("</div>")
    out = day / "menu.html"
    out.write_text("\n".join(h), encoding="utf-8")
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    date_str = args[0] if args else datetime.date.today().isoformat()
    if "--menu" in sys.argv:
        print(render_menu(date_str))
    else:
        print(render(date_str))
