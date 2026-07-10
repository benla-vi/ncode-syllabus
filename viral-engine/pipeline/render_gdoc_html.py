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


BEAT_LABELS = {
    "hook": "הוק", "tension": "מתח", "story": "הסיפור",
    "value": "הערך — איך זה נוגע אליך", "loop_close": "סגירת הלופ",
    "cta": "קריאה לפעולה", "engagement": "אינגייג'מנט",
}
# צבע רקע לתווית כל ביט — עוזר לעין לתפוס מבנה
BEAT_COLOR = {
    "hook": "#ffe08a", "tension": "#ffd0a6", "story": "#cfe8ff",
    "value": "#d6f5d6", "loop_close": "#e6d6ff", "cta": "#ffc9de",
    "engagement": "#d9d9d9",
}
BIG_RULE = ('<p style="font-size:16pt;color:#999;letter-spacing:2px;margin:6px 0">'
            '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</p>')


def _hooks_block(h, s):
    """הוק מומלץ גדול בקופסה, ואז אלטרנטיבות קטנות."""
    hooks = s.get("hooks", [])
    rec_family = hooks[0] if hooks else {}
    # ההוק המומלץ = האופציה הראשונה של המשפחה הראשונה
    if "text" in rec_family:                     # תאימות לאחור
        rec_text, rec_name = rec_family.get("text", ""), rec_family.get("type", "")
        rec_loop = ""
    else:
        opts = rec_family.get("options", [])
        rec_text = opts[0] if opts else ""
        rec_name, rec_loop = rec_family.get("family", ""), rec_family.get("loop", "")

    h.append('<p style="font-size:11pt;color:#c0392b;font-weight:bold;margin-bottom:2px">▶ ההוק — מה שאומרים בשנייה הראשונה</p>')
    h.append(f'<p style="font-size:15pt;font-weight:bold;background:#fff3cd;'
             f'padding:12px 14px;border-right:5px solid #f0ad4e;line-height:1.5">{esc(rec_text)}</p>')
    if rec_loop:
        h.append(f'<p style="font-size:9.5pt;color:#8a6d3b">🔓 הלופ נסגר בביט "סגירת הלופ" למטה.</p>')
    # שאר אופציות ההוק נשמרות ב-JSON/ClickUp ל-A/B — לא מציגים כאן כדי לא להעמיס.


def render(date_str: str) -> Path:
    day = OUTPUT / date_str
    scripts = [json.loads(p.read_text(encoding="utf-8"))
               for p in sorted(day.glob("script-*.json"), key=_script_sort_key)]

    total = len(scripts)
    h = [f'<div dir="rtl" style="line-height:1.6;font-size:11.5pt">',
         f'<h1>🎬 תסריטים ליום צילום — {esc(date_str)}</h1>',
         f'<p style="color:#666">{total} סרטונים · פורמט טלפרומפטר · '
         f'מה שמודגש בצהוב = מה שאומרים; אפור קטן = הערות הפקה.</p>']

    for i, s in enumerate(scripts, 1):
        h.append(BIG_RULE)
        h.append(f'<h1 style="background:#111;color:#fff;padding:8px 12px">🎬 סרטון {i} מתוך {total}</h1>')
        h.append(f'<h2 style="margin-top:4px">{esc(s.get("title"))}</h2>')
        h.append(f'<p style="color:#555;font-size:10.5pt"><b>⏱ משך:</b> ~{esc(s.get("duration_sec","?"))} שנ׳ '
                 f'&nbsp;·&nbsp; <b>💬 מילת תגובה:</b> {esc(s.get("comment_word"))} '
                 f'&nbsp;·&nbsp; <b>🎁 מתנה:</b> {esc(s.get("gift",{}).get("name"))}</p>')

        fmt = s.get("format") or {}
        if fmt:
            h.append(f'<p style="background:#e8f6ee;border-right:5px solid #2e9e5b;padding:8px 12px;font-size:10.5pt">'
                     f'<b>🎛 פורמט: {esc(fmt.get("name"))}</b><br>'
                     f'📱 <b>מה מצלמים:</b> {esc(fmt.get("filming"))}<br>'
                     f'✂️ <b>מה העורך בונה:</b> {esc(fmt.get("editing"))}</p>')

        _hooks_block(h, s)

        # --- התסריט כטלפרומפטר אנכי ---
        h.append('<p style="font-size:13pt;font-weight:bold;margin-top:14px;border-bottom:2px solid #111;padding-bottom:2px">📝 התסריט</p>')
        for b in s.get("script", []):
            beat = b.get("beat", "")
            label = BEAT_LABELS.get(beat, beat)
            color = BEAT_COLOR.get(beat, "#eee")
            h.append(f'<p style="margin:12px 0 2px"><span style="background:{color};'
                     f'padding:2px 10px;font-weight:bold;font-size:10pt">{esc(label)}</span>'
                     f'<span style="color:#999;font-size:9pt">&nbsp;&nbsp;{esc(b.get("sec",""))}</span></p>')
            h.append(f'<p style="font-size:14pt;line-height:1.5;margin:2px 0 4px">{esc(b.get("text"))}</p>')
            if b.get("visual"):
                h.append(f'<p style="font-size:9pt;color:#999;margin:0 0 6px">🎥 {esc(b.get("visual"))}</p>')

        # --- אריזת הפרסום ---
        h.append('<p style="font-size:13pt;font-weight:bold;margin-top:14px;border-bottom:2px solid #111;padding-bottom:2px">🚀 לפרסום</p>')
        if s.get("caption"):
            h.append('<p style="font-size:10pt;color:#666;margin-bottom:1px"><b>קפשן:</b></p>')
            h.append(f'<p style="background:#f6f6f6;padding:10px;font-size:11pt">{esc(s.get("caption")).replace(chr(10), "<br>")}</p>')
        if s.get("onscreen_text"):
            h.append('<p style="font-size:10pt;color:#666;margin-bottom:1px"><b>טקסטים על המסך:</b></p><ul style="font-size:10.5pt">')
            h += [f"<li>{esc(t)}</li>" for t in s["onscreen_text"]]
            h.append("</ul>")
        if s.get("dm_message"):
            h.append('<p style="font-size:10pt;color:#666;margin-bottom:1px"><b>הודעת DM אוטומטית (ManyChat):</b></p>')
            h.append(f'<p style="background:#eef6ff;padding:10px;font-size:10.5pt">{esc(s.get("dm_message")).replace(chr(10), "<br>")}</p>')
        if s.get("funnel_next_step"):
            h.append(f'<p style="font-size:10pt;color:#666"><b>המשך פאנל:</b> {esc(s.get("funnel_next_step"))}</p>')

        # --- לוודא לפני צילום (עובדות + דגלי סיכון ביחד) ---
        verify, seen = [], set()
        notes = s.get("critic_notes") or {}
        for v in list(s.get("facts_to_verify", [])) + notes.get("risk_flags", []):
            key = "".join(str(v).split())[:40]          # דה-דופ גס לפי תחילת המשפט
            if key and key not in seen:
                seen.add(key)
                verify.append(v)
        if verify:
            h.append('<p style="font-size:11pt;font-weight:bold;color:#c0392b;margin-top:12px">⚠️ לוודא לפני שאומרים במצלמה</p>')
            h.append('<ul style="font-size:10pt;color:#a94442">')
            h += [f"<li>☐ {esc(v)}</li>" for v in verify]
            h.append("</ul>")

    h.append(BIG_RULE)
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
        outlier = st.get("source_outlier") or {}
        if outlier:
            meta = " · ".join(x for x in [esc(outlier.get("page")),
                                          esc(outlier.get("views")),
                                          esc(outlier.get("engagement"))] if x)
            h.append('<p style="background:#f0e6ff;border-right:4px solid #7d3cff;'
                     'padding:8px 10px;font-size:10.5pt">'
                     f'<b>🧬 פורמט מוכח</b> ({meta})<br>'
                     f'<b>ההוק המקורי:</b> {esc(outlier.get("original_hook"))}<br>'
                     f'<b>איך מותחים לנישה:</b> {esc(outlier.get("stretch_suggestion"))}</p>')
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
