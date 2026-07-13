---
dir: rtl
lang: he
---

# העברת viral-engine לריפו עצמאי — צ'קליסט לבן

המטרה: להוציא את `viral-engine/` לריפו פרטי משלו, שכל משתף-פעולה יוכל לפתוח סשן
Claude Code עליו ולקבל אותו סוכן בדיוק. הריפו הזה **הוא הסוכן**.

---

## 1. יצירת הריפו הפרטי (2 דקות)
1. היכנס ל-**github.com** → כפתור **+** למעלה מימין → **New repository**.
2. **Owner:** `benla-vi` · **Repository name:** `viral-engine`.
3. סמן **Private**. **אל תסמן** "Add a README" / .gitignore / license (הריפו יגיע מלא מהעתקה).
4. לחץ **Create repository**. השאר את הדף פתוח — הוא מראה את כתובת ה-remote.

## 2. הוספת משתף-פעולה
1. בריפו החדש: **Settings** → **Collaborators** (בתפריט הצד) → **Add people**.
2. הזן שם-משתמש/אימייל של החבר → **Add**. הוא יקבל הזמנה במייל ויאשר.

## 3. העתקת התוכן לריפו החדש (סשן Claude Code)
פתח **סשן Claude Code חדש שיש לו גישה לשני הריפו** (הישן `ncode-syllabus` והחדש
`viral-engine`), והדבק את ההוראה הזו **מילה במילה**:

> העתק את תוכן viral-engine/ מהריפו ncode-syllabus לשורש הריפו viral-engine, קומיט ופוש

⚠️ **חשוב — `.gitignore` של הריפו החדש חייב לא להתעלם מ-`output/`.**
ב-ncode-syllabus כלל ההתעלמות מ-`output/` יושב ב-`.gitignore` של **שורש** הריפו הישן
(מחוץ ל-viral-engine), ולכן הוא **לא נוסע** בהעתקה. הקובץ `viral-engine/.gitignore`
כבר מוגדר כך ש-`output/` **מקומט** (מתעלם רק מ-`__pycache__`, venv, לוגים). ודא
שהוא הגיע לשורש הריפו החדש ושתיקיות `output/<date>/` אכן נכנסות לקומיט.

## 4. אימות
1. פתח **סשן Claude Code על הריפו החדש** (`viral-engine`).
2. ודא ש-`CLAUDE.md` נטען אוטומטית (הסוכן "יודע" מה זה viral-engine).
3. הרץ `/run-round` — צריך להפיק תפריט ולפרסם דף Artifact.
4. הרץ `python pipeline/test_pipeline.py` — חייב ירוק.

## 5. מה נשאר מאחור
**המוח השני והסילבוס נשארים פרטיים בריפו הישן** (`ncode-syllabus`). הריפו החדש
מכיל **רק את הידע המזוקק** שכבר יושב תחת `viral-engine/knowledge/` — לא את מסמכי
המקור המלאים. אין תלות בין הריפו החדש לישן אחרי ההעתקה.
