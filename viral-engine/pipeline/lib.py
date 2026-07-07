"""ספריית בסיס משותפת לכל הסוכנים — טעינת קונפיג, פרומפטים, וקריאות לקלוד."""
import json
import re
from pathlib import Path
from string import Template

import yaml
from anthropic import Anthropic

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "prompts"
KNOWLEDGE = ROOT / "knowledge"
OUTPUT = ROOT / "output"

client = Anthropic()


def load_config() -> dict:
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_prompt(name: str, **fmt) -> str:
    """טוען קובץ פרומפט וממלא משתני ${placeholder}. משתנה חסר נשאר כמו שהוא.

    משתמש ב-string.Template במקום str.format_map כדי לא להתנגש עם בלוקי
    JSON לדוגמה שמכילים סוגריים מסולסלים בתוך הפרומפטים.
    """
    text = (PROMPTS / name).read_text(encoding="utf-8")
    return Template(text).safe_substitute({k: str(v) for k, v in fmt.items()})


def load_knowledge(rel: str, fallback: str = "") -> str:
    """טוען קובץ ידע יחסי לתיקיית knowledge/. מחזיר fallback אם הקובץ לא קיים."""
    p = KNOWLEDGE / rel
    return p.read_text(encoding="utf-8") if p.exists() else fallback


def system_prompt(cfg: dict) -> str:
    return load_prompt(
        "00-system-core.md",
        creator_name=cfg["creator"]["name"],
        creator_handle=cfg["creator"]["handle"],
        niche=cfg["creator"]["niche"],
        audience=cfg["creator"]["audience"].strip(),
        tone=cfg["creator"]["tone"].strip(),
    )


def load_style_guide(which: str = "organic") -> str:
    """טוען מדריך סגנון שנוצר ע"י ingest_style.py. which: organic / ads."""
    path = KNOWLEDGE / "style" / f"style-{which}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "(עדיין לא נוצר מדריך סגנון — ראה הוראות ב-README)"


def model_for(cfg: dict, agent: str) -> str:
    """בוחר מודל לפי הסוכן: זול לאיסוף/דירוג, חזק לכתיבה. ראה config.yaml → model."""
    m = cfg["model"]
    return m.get("per_agent", {}).get(agent) or m.get("default") or m.get("id", "claude-sonnet-5")


def ask_claude(cfg: dict, system: str, user: str, web_search: bool = False,
               max_tokens: int = 32000, agent: str = "") -> str:
    """קריאה לקלוד עם סטרימינג. מחזיר את הטקסט המלא."""
    kwargs = dict(
        model=model_for(cfg, agent),
        max_tokens=max_tokens,
        thinking={"type": "adaptive"},
        output_config={"effort": cfg["model"].get("effort", "high")},
        system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user}],
    )
    if web_search:
        kwargs["tools"] = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 15}]

    with client.messages.stream(**kwargs) as stream:
        response = stream.get_final_message()

    return "".join(b.text for b in response.content if b.type == "text")


def extract_json(text: str):
    """מחלץ JSON מתשובת מודל — גם אם עטוף ב-```json או בטקסט מסביב."""
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    # מציאת האובייקט/מערך הראשון
    start = min((i for i in (text.find("{"), text.find("[")) if i != -1), default=-1)
    if start == -1:
        raise ValueError("לא נמצא JSON בתשובה:\n" + text[:500])
    decoder = json.JSONDecoder()
    obj, _ = decoder.raw_decode(text[start:])
    return obj
