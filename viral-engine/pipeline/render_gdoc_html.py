"""ממיר את תוצרי ריצה יומית ל-HTML מעוצב (RTL) שמוכן להמרה לגוגל דוקס.

שימוש:  python pipeline/render_gdoc_html.py [YYYY-MM-DD]   (ברירת מחדל: היום)
פלט:    output/<date>/brief.html
"""
import datetime
import html
import json
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


def render(date_str: str) -> Path:
    day = OUTPUT / date_str
    scripts = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(day.glob("script-*.json"))]
    ranking = {}
    rp = day / "02-ranking.json"
    if rp.exists():
        ranking = json.loads(rp.read_text(encoding="utf-8"))

    h = [f'<div dir="rtl"><h1>▶ בריף תוכן יומי — {esc(date_str)}</h1>']
    if ranking.get("rejected_summary"):
        h.append(f'<p><b>למה נפסלו השאר:</b> {esc(ranking["rejected_summary"])}</p>')

    for i, s in enumerate(scripts, 1):
        h.append(f'<h1>סרטון {i}: {esc(s.get("title"))}</h1>')
        h.append(f'<p><b>משך:</b> ~{esc(s.get("duration_sec","?"))} שניות &nbsp;|&nbsp; '
                 f'<b>מילת תגובה:</b> {esc(s.get("comment_word"))} &nbsp;|&nbsp; '
                 f'<b>מתנה:</b> {esc(s.get("gift",{}).get("name"))}</p>')

        h.append("<h2>הוקים (בחר אחד)</h2><ul>")
        for hk in s.get("hooks", []):
            h.append(f'<li><b>[{esc(hk.get("type"))}]</b> {esc(hk.get("text"))}</li>')
        h.append("</ul>")

        h.append("<h2>התסריט</h2>")
        h.append('<table border="1" cellpadding="6" style="border-collapse:collapse">'
                 "<tr><th>זמן</th><th>ביט</th><th>מה אומרים</th><th>איך מגישים</th><th>מה על המסך</th></tr>")
        for b in s.get("script", []):
            h.append(f'<tr><td>{esc(b.get("sec"))}</td><td>{esc(b.get("beat"))}</td>'
                     f'<td>{esc(b.get("text"))}</td><td>{esc(b.get("delivery"))}</td>'
                     f'<td>{esc(b.get("visual"))}</td></tr>')
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


if __name__ == "__main__":
    date_str = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
    print(render(date_str))
