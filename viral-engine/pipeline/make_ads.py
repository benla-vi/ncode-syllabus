"""יצירת קריאייטיבים לממומן.

שימוש:
    python pipeline/make_ads.py --offer base44_webinar          # לפי id מה-config
    python pipeline/make_ads.py --offer-text "תיאור חופשי של ההצעה"
    python pipeline/make_ads.py --offer paid_course --num 5
"""
import argparse
import datetime
import json
import sys

from lib import OUTPUT, ask_claude, extract_json, load_config, load_prompt, load_style_guide, system_prompt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--offer", help="id של פאנל מתוך config.yaml")
    parser.add_argument("--offer-text", help="תיאור חופשי של ההצעה")
    parser.add_argument("--num", type=int, default=3, help="כמה וריאציות")
    args = parser.parse_args()

    cfg = load_config()
    if args.offer:
        match = [f for f in cfg["funnels"] if f["id"] == args.offer]
        if not match:
            print("לא נמצא פאנל עם id כזה. אפשרויות:", ", ".join(f["id"] for f in cfg["funnels"]))
            return 1
        offer = json.dumps(match[0], ensure_ascii=False, indent=2)
    elif args.offer_text:
        offer = args.offer_text
    else:
        print("חובה לציין --offer או --offer-text")
        return 1

    system = system_prompt(cfg)
    prompt = load_prompt("04-ad-writer.md", num_ads=args.num,
                         ads_style_guide=load_style_guide("ads"))
    user = prompt + "\n\n## ההצעה\n" + offer

    print(f"📢  כותב {args.num} קריאייטיבים לממומן...")
    result = extract_json(ask_claude(cfg, system, user, agent="ads"))

    out_dir = OUTPUT / datetime.date.today().isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"ads-{args.offer or 'custom'}.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    # רנדור לקריאה נוחה
    lines = [f"# קריאייטיבים לממומן — {result.get('offer','')}", ""]
    for ad in result.get("ads", []):
        lines += [f"## {ad.get('name','')} ({ad.get('angle','')})", "",
                  f"**קהל:** {ad.get('target','')} | **משך:** ~{ad.get('duration_sec','?')} שנ'", "",
                  "| זמן | ביט | טקסט | על המסך | ויז'ואל |", "|---|---|---|---|---|"]
        for b in ad.get("script", []):
            lines += [f"| {b.get('sec','')} | {b.get('beat','')} | {b.get('text','')} | {b.get('onscreen','')} | {b.get('visual','')} |"]
        lines += ["", f"**Primary Text:**\n\n```\n{ad.get('primary_text','')}\n```", "",
                  f"**Headline:** {ad.get('headline','')}", ""]
        if ad.get("policy_notes"):
            lines += [f"⚠️ **מדיניות:** {ad['policy_notes']}", ""]
    md_path = out_dir / f"ads-{args.offer or 'custom'}.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"✅  מוכן: {md_path}")


if __name__ == "__main__":
    sys.exit(main())
