---
name: write-scripts
description: כותב תסריטים מלאים לסיפורים שבעל-הבית בחר בתפריט (למשל /write-scripts 7,11,16) — תסריטאי Opus לכל סיפור, מבקר-באצ' Opus עם אכיפת אנטי-חזרתיות, בודק-עובדות Sonnet, ופרסום התסריטים כדף Artifact. השתמש אחרי שבעל-הבית אמר מספרים בצ'אט.
---

# /write-scripts <מספרים> — כתיבת הנבחרים

אתה **המתזמר**. אתה שולח סוכנים ומעביר payloads — **לא כותב תסריט בעצמך**.
קלט: המספרים שבעל-הבית אמר (למשל `7,11,16`). כל מספר = `id` בתפריט הראונד.
דרוש שהראונד (`/run-round`) כבר רץ ויש `output/<date>/01-stories.json` + `02-ranking.json`.

קרא `CLAUDE.md` ו-`docs/GLOSSARY.md` אם לא קראת.

---

## פיצול מודלים (קדוש)
- **תסריטאי = Opus. מבקר = Opus.** (הלב — שווה את ההפרש.)
- **בודק-עובדות = Sonnet.** (אימות = הרבה חיפושים, מהיר.)
- **אף פעם לא כותבים קופי במודל המתזמר.**

---

## שלב 0 — טעינה
1. `git pull` על main.
2. אתר את `<date>` (התיקייה המתוארכת האחרונה עם `01-stories.json`).
3. טען `01-stories.json` + `02-ranking.json`. חלץ את הסיפורים לפי ה-`id`-ים שנבחרו + הערות המדרג התואמות.

## שלב 1 — בניית ה-payload לתסריטאי (כמו `write_script` ב-`run_daily.py`)
לכל סיפור נבחר בנה את הפרומפט דרך שרשרת `lib.load_prompt` — **שכבת הקול קודם**:
- **שכבה 1 (מחייב, גובר):** `knowledge/style/ben-voice.md`.
- **שכבה 2:** מדריך הסגנון האורגני (`load_style_guide("organic")`).
- הזרק `brand_context` (`knowledge/brand/ncode.md`), `audience_context` (`knowledge/audience/ai-goldrush.md`), `production_formats` (`knowledge/formats/proven-formats.md`), `lead_magnets` ו-`comment_triggers` מ-`config.yaml`.
- ה-prompt: **הגרסה מ-`config.yaml → prompts.scriptwriter`** (ברירת מחדל `03-scriptwriter.md`, v2 פורמט-תחילה).
- צרף לכל סיפור: אובייקט הסיפור, הערות המדרג, ו-`config.funnels`.

הדרך הפשוטה: הרץ את הלוגיקה של `run_daily.write_script` (אותה שרשרת `load_prompt`) לבניית ה-user prompt — ואז שלח אותו לסוכן Opus במקום ל-`ask_claude`.

## שלב 2 — תסריטאי: סוכן Opus לכל סיפור
- שגר **סוכן Opus אחד לכל תסריט** (במקביל, בהודעה אחת), עם ה-payload שבנית.
- כל סוכן מחזיר JSON תסריט לפי הסכימה של `prompts/03-scriptwriter.md` (format, hooks, script beats, retention, dm_message, caption, facts_to_verify).

## שלב 3 — מבקר-באצ' (Opus, אכיפת אנטי-חזרתיות)
- שגר **סוכן מבקר Opus אחד שרואה את כל התסריטים יחד** (לפי `prompts/05-critic.md`).
- דרוש ממנו במפורש **אנטי-חזרתיות חוצת-תסריטים:** גשר, סגירת לופ, פורמט הפקה ופתיחה — מגוונים בין תסריטי אותו יום. אם שניים דומים — שכתב אחד.
- מחזיר את כל התסריטים המתוקנים + `critic_notes` (hook_verdict, changes, risk_flags).

## שלב 4 — בודק-עובדות: סוכן 7 (Sonnet, לכל תסריט)
- שגר **סוכן Sonnet לכל תסריט** לפי `prompts/07-fact-checker.md`, עם התסריט + מקורות הסקאוט.
- מדרג Tier: Tier 1 עובדה · Tier 2 "לפי הדיווחים" · **Tier 3 דיווח-עצמי = חובה ייחוס, אסור פאיוף בלי "לפי האתר שלהם".**
- **החל את התיקונים** על התסריט. `verdict=blocked` ⇒ אסור לצלם — סמן blockers בבירור לבעל-הבית.
- שמור כל תסריט סופי ל-`output/<date>/script-NN.json` (NN = ה-`id`).

## שלב 5 — רינדור הבריף
```
python pipeline/render_gdoc_html.py <date>
```
מייצר `output/<date>/brief.html` (טלפרומפטר RTL, הוק מודגש, הערות הפקה).

## שלב 6 — פרסום כ-Artifact + קומיט
- פרסם את `output/<date>/brief.html` בכלי **Artifact** (favicon 🎬, title "תסריטים <date>").
- **אסור קובץ להורדה. אסור ClickUp.** רק לינק ה-Artifact.
- `git add output/<date>` וקומיט ("תסריטים <date>: <ids>").
- מסור לבעל-הבית את הלינק, וציין אם יש `blocked`/blockers שדורשים החלטה לפני צילום.
