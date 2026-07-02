"""מוריד ומתמלל סרטונים — להרצה **במחשב שלך**, לא בסביבה הזאת (שם אין גישת רשת לרשתות חברתיות).

התקנה חד-פעמית:
    pip install yt-dlp openai-whisper

שימוש:
    # סרטון בודד → תמלול לתיקיית ben
    python local_transcribe.py --url "https://www.instagram.com/reels/DPlQ-5tiIY2/" --category ben

    # כמה סרטונים של טל בבת אחת
    python local_transcribe.py --category tal \
        --url "https://www.instagram.com/reel/AAA/" \
        --url "https://www.instagram.com/reel/BBB/"

    # קובץ וידאו שכבר יש לך על הדיסק (למשל סרטוני המכירה מהוואטסאפ)
    python local_transcribe.py --file ~/Downloads/tal-ad-1.mp4 --category ads
    python local_transcribe.py --file ~/Downloads/tal-ad-2.mp4 --category ads

התוצאה: קבצי .txt בתיקייה knowledge/transcripts/<category>/ (יחסית לתיקיית viral-engine),
בדיוק במבנה שה-pipeline מצפה לו. אחרי שיש לך כמה קבצים, תעלה את כל תיקיית
knowledge/transcripts/ (או פשוט תדביק את התוכן) בחזרה לצ'אט, ואני ארוץ את
ingest_style.py כדי לבנות את מדריך הסגנון.

הערה: whisper עם --model large-v3 נותן את איכות התמלול העברי הכי טובה, אבל
דורש GPU/כמה דקות ב-CPU. --model medium מהיר משמעותית ועדיין סביר לעברית.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent  # viral-engine/
OUT_BASE = REPO_ROOT / "knowledge" / "transcripts"


def run(cmd: list[str]) -> None:
    print("→", " ".join(cmd))
    subprocess.run(cmd, check=True)


def download(url: str, workdir: Path) -> Path:
    out_tmpl = str(workdir / "%(id)s.%(ext)s")
    run(["yt-dlp", "-f", "mp4/best", "-o", out_tmpl, url])
    candidates = sorted(workdir.glob("*.mp4")) or sorted(workdir.glob("*"))
    if not candidates:
        raise SystemExit(f"לא נמצא קובץ שהורד עבור {url}")
    return candidates[-1]


def transcribe(video_path: Path, workdir: Path, model: str) -> str:
    run(["whisper", str(video_path), "--language", "Hebrew", "--model", model,
         "--output_format", "txt", "--output_dir", str(workdir)])
    txt_path = video_path.with_suffix(".txt")
    if not txt_path.exists():
        # whisper weirdly sometimes drops extra suffixes; fall back to any .txt written
        found = sorted(workdir.glob("*.txt"))
        if not found:
            raise SystemExit("whisper לא הפיק קובץ txt")
        txt_path = found[-1]
    return txt_path.read_text(encoding="utf-8")


def save(category: str, name: str, text: str, source: str) -> Path:
    out_dir = OUT_BASE / category
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{name}.txt"
    header = f"מקור: {source}\n---\n\n"
    out_path.write_text(header + text.strip() + "\n", encoding="utf-8")
    return out_path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", action="append", default=[], help="קישור לריל/טיקטוק (אפשר כמה פעמים)")
    p.add_argument("--file", action="append", default=[], help="קובץ וידאו מקומי (אפשר כמה פעמים)")
    p.add_argument("--category", required=True, choices=["tal", "ben", "ads"])
    p.add_argument("--model", default="medium", help="גודל מודל whisper: tiny/base/small/medium/large-v3")
    args = p.parse_args()

    if not args.url and not args.file:
        p.error("צריך לפחות --url אחד או --file אחד")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        for i, url in enumerate(args.url, 1):
            print(f"\n📥  מוריד {i}/{len(args.url)}: {url}")
            video = download(url, workdir)
            print("🎙️  מתמלל...")
            text = transcribe(video, workdir, args.model)
            out = save(args.category, video.stem, text, url)
            print(f"✅  נשמר: {out}")

        for i, file_str in enumerate(args.file, 1):
            video = Path(file_str).expanduser().resolve()
            if not video.exists():
                print(f"⚠️   לא נמצא: {video}")
                continue
            print(f"\n🎙️  מתמלל {i}/{len(args.file)}: {video.name}")
            text = transcribe(video, workdir, args.model)
            out = save(args.category, video.stem, text, str(video))
            print(f"✅  נשמר: {out}")

    print(f"\n🎉  סיימתי. הקבצים נמצאים ב-{OUT_BASE}/{args.category}/")
    print("עכשיו: העלה/י את התוכן שלהם לצ'אט (או את התיקייה כולה) כדי שאבנה את מדריך הסגנון.")


if __name__ == "__main__":
    sys.exit(main())
