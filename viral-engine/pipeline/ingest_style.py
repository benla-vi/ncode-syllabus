"""בניית מדריכי סגנון מתמלולים.

שים תמלולים (קבצי .txt או .md) בתיקיות:
    knowledge/transcripts/tal/   — סרטונים אורגניים של טל רוטר
    knowledge/transcripts/ben/   — הסרטונים שלך
    knowledge/transcripts/ads/   — סרטוני מכירה/ממומן (למשל השניים מהוואטסאפ)

ואז הרץ:
    python pipeline/ingest_style.py            # בונה את שני המדריכים
    python pipeline/ingest_style.py --only ads # רק מדריך המכירה

טיפ לתמלול: אם יש לך רק קבצי וידאו, אפשר לתמלל עם whisper:
    pip install openai-whisper && whisper video.mp4 --language he --model large-v3
"""
import argparse
import sys

from lib import KNOWLEDGE, ask_claude, load_config, load_prompt, system_prompt


def collect(folders: list[str]) -> str:
    chunks = []
    for folder in folders:
        d = KNOWLEDGE / "transcripts" / folder
        for f in sorted(d.glob("*")):
            if f.suffix.lower() in (".txt", ".md") and f.name.lower() != "readme.md":
                chunks.append(f"### תמלול: {folder}/{f.name}\n\n{f.read_text(encoding='utf-8')}")
    return "\n\n---\n\n".join(chunks)


def build(cfg, system, which: str, folders: list[str], extra: str):
    corpus = collect(folders)
    if not corpus.strip():
        print(f"⏭️   אין תמלולים עבור '{which}' (תיקיות: {folders}) — מדלג.")
        return
    print(f"🧬  ממדל סגנון '{which}' מתוך {corpus.count('### תמלול')} תמלולים...")
    prompt = load_prompt("06-style-modeler.md", creator_name=cfg["creator"]["name"])
    user = prompt + f"\n\n{extra}\n\n## התמלולים\n\n{corpus}"
    guide = ask_claude(cfg, system, user, max_tokens=48000, agent="style_modeler")
    out = KNOWLEDGE / "style" / f"style-{which}.md"
    out.write_text(guide, encoding="utf-8")
    print(f"✅  נשמר: {out}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=["organic", "ads"], help="לבנות רק מדריך אחד")
    args = parser.parse_args()

    cfg = load_config()
    system = system_prompt(cfg)

    if args.only in (None, "organic"):
        build(cfg, system, "organic", ["tal", "ben"],
              "הקשר: אלה תמלולים של סרטונים אורגניים ויראליים. "
              "אם יש תמלולים גם של טל וגם של בן — שים לב להבדלים וציין אותם, "
              "אבל בנה מדריך אחד שמשלב את החוזקות של שניהם עבור בן.")
    if args.only in (None, "ads"):
        build(cfg, system, "ads", ["ads"],
              "הקשר: אלה תמלולים של סרטוני מכירה לקמפיינים ממומנים. "
              "התמקד בסעיף טכניקות השכנוע: מבנה המכירה, טיפול בהתנגדויות, בניית דחיפות.")


if __name__ == "__main__":
    sys.exit(main())
