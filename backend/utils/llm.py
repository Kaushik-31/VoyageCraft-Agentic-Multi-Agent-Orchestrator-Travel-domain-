from __future__ import annotations
from .config import get_settings, choose_llm
import json
import re
from typing import Any, Dict, List, Sequence
import httpx

# -------------------- Provider calls --------------------

def _openai_chat(system: str, user: str, model: str, api_key: str, temperature: float = 0.3) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": temperature,
    }
    r = httpx.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]  # type: ignore[index]


def _ollama_chat(system: str, user: str, model: str, host: str, temperature: float = 0.3) -> str:
    # Ollama HTTP API
    url = f"{host.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "options": {"temperature": temperature},
    }
    r = httpx.post(url, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict) and "message" in data and "content" in data["message"]:
        return data["message"]["content"]
    return data.get("content", "")

# -------------------- Public helpers --------------------

def _call_llm(system: str, user: str, temperature: float | None = None) -> str:
    s = get_settings()
    picked = choose_llm(s)
    if not picked:
        return ""
    kind, cfg = picked
    temp = s.LLM_TEMPERATURE if temperature is None else temperature
    if kind == "openai":
        return _openai_chat(system, user, cfg["model"], cfg["api_key"], temp)
    if kind == "ollama":
        return _ollama_chat(system, user, cfg["model"], cfg["host"], temp)
    return ""


def _extract_json_list(text: str) -> list:
    """Extract a JSON array from free text robustly."""
    if not text:
        return []
    # try direct parse
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass
    # try array substring
    m = re.search(r"\[[\s\S]*\]", text)
    if m:
        try:
            parsed = json.loads(m.group(0))
            if isinstance(parsed, list):
                return parsed
        except Exception:
            return []
    return []


def ranked_spots_via_llm(
    destination: str,
    interests: Sequence[str] | None,
    days: int,
    month: str | None = None,
    max_items: int = 12,
) -> List[Dict[str, Any]]:
    """
    Ask the LLM for the BEST places/experiences in a destination, aligned to interests and ready to schedule.
    Returns a list of JSON objects with rich metadata (title, neighborhood, category, best_time, duration, price, reason).
    If no LLM is configured or parsing fails, returns [].
    """
    ints = ", ".join(interests or [])
    system = (
        "You are a senior travel curator for a world-class guide. "
        "Only output valid JSON. Do not include explanations, disclaimers, or markdown."
    )
    user = (
        f"Destination: {destination}\n"
        f"Trip length (days): {days}\n"
        f"Interests: {ints if ints else 'none'}\n"
        f"Month: {month or 'auto'}\n\n"
        "TASK:\n"
        "- Propose top places/experiences that a discerning visitor should not miss.\n"
        "- Prefer high-signal items (landmarks, major museums, iconic viewpoints, notable neighborhoods/markets, "
        "  standout food/cafe areas); avoid generic tourist traps unless truly iconic.\n"
        "- Align to the given interests.\n"
        "- Distribute across different neighborhoods when possible and vary time-of-day (morning/afternoon/evening).\n"
        "- Keep each title short and specific. If unsure on a field, omit it.\n\n"
        "OUTPUT STRICTLY AS JSON ARRAY of objects with this schema (no prose):\n"
        "[\n"
        "  {\n"
        '    "title": "string",\n'
        '    "neighborhood": "string (optional)",\n'
        '    "category": "museum | landmark | neighborhood | market | cafe | park | gallery | viewpoint | other",\n'
        '    "best_time": "morning | afternoon | evening | night | flexible (optional)",\n'
        '    "duration_hours":  number (e.g., 1.5),\n'
        '    "est_price": number (USD, 0 if free, omit if unknown),\n'
        '    "reason_short": "1 sentence focusing on why this is exceptional"\n'
        "  }\n"
        "]\n"
        f"Return at most {max_items} items."
    )

    try:
        raw = _call_llm(system, user)
    except Exception:
        return []

    items = _extract_json_list(raw)
    out: List[Dict[str, Any]] = []
    seen = set()
    for it in items:
        if not isinstance(it, dict):
            continue
        title = str(it.get("title", "")).strip()
        if not title or title.lower() in seen:
            continue
        seen.add(title.lower())
        out.append(
            {
                "title": title,
                "neighborhood": (it.get("neighborhood") or "").strip() or None,
                "category": (it.get("category") or "other").strip(),
                "best_time": (it.get("best_time") or "flexible").strip(),
                "duration_hours": float(it.get("duration_hours", 1.5)),
                "est_price": (float(it["est_price"]) if "est_price" in it else None),
                "reason_short": (it.get("reason_short") or "").strip() or None,
            }
        )
        if len(out) >= max_items:
            break
    return out


def flatten_spots_to_activity_strings(spots: Sequence[Dict[str, Any]]) -> List[str]:
    """
    Turn rich spot objects into concise activity strings for our current Plan schema.
    Example: 'Musée d'Orsay (Left Bank) — morning • 2h'
    """
    acts: List[str] = []
    for s in spots:
        title = s.get("title") or ""
        nbh = s.get("neighborhood")
        bt = s.get("best_time")
        dur = s.get("duration_hours")
        bits = [title]
        suffix: List[str] = []
        if nbh:
            bits.append(f"({nbh})")
        if bt and isinstance(bt, str):
            suffix.append(bt)
        if isinstance(dur, (int, float)):
            hrs = round(float(dur), 1)
            suffix.append(f"{hrs}h")
        if suffix:
            bits.append(" — " + " • ".join(suffix))
        sstr = " ".join(bits).strip()
        if sstr:
            acts.append(sstr)
    # Dedupe while preserving order
    seen = set()
    out: List[str] = []
    for a in acts:
        if a not in seen:
            out.append(a)
            seen.add(a)
    return out
