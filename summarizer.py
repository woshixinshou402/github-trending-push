import json
import re
import requests
from config import LLM_API_KEY, LLM_API_BASE, LLM_MODEL, DEBUG

SYSTEM_PROMPT = """You are a tech trend analyst. Given today's GitHub Trending repositories data, write a concise daily report in Chinese (中文).

Return ONLY valid JSON, no other text:
{
  "summary": "2-3 sentence overview of today's trending themes and notable patterns (in Chinese, under 200 chars)",
  "highlights": [
    {"name": "owner/repo", "reason": "one-line reason this repo is worth attention (Chinese, under 50 chars)"}
  ]
}

Rules:
- Pick 3-5 highlights that are truly interesting or fast-growing
- summary should capture the big picture: what kinds of repos are trending, any emerging themes
- Be specific, not generic. Reference actual repo names and what they do."""


def build_prompt(repos_data: dict) -> str:
    """Build a prompt from classified repo data."""
    lines = ["Today's GitHub Trending repositories:\n"]

    for lang_tag, repos in repos_data.get("by_language", {}).items():
        if not repos:
            continue
        lines.append(f"--- {lang_tag or 'All Languages'} ---")
        for r in repos:
            name = r.get("fullname", "")
            desc = r.get("description", "")
            stars = r.get("stars", 0)
            added = r.get("added_stars", 0)
            lines.append(f"- {name} | ⭐{stars} (+{added}) | {desc}")

    return "\n".join(lines)


def summarize(repos_data: dict) -> dict | None:
    """Call LLM to generate a summary of trending repos.

    Returns {"summary": str, "highlights": list} or None if LLM is unavailable.
    """
    if not LLM_API_KEY:
        if DEBUG:
            print("  [summarize] No LLM_API_KEY configured, skipping AI summary")
        return None

    prompt = build_prompt(repos_data)
    if DEBUG:
        print(f"  [summarize] Prompt length: {len(prompt)} chars")

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 800,
    }

    try:
        resp = requests.post(
            f"{LLM_API_BASE}/chat/completions",
            headers=headers,
            json=body,
            timeout=60,
        )
        if resp.status_code != 200:
            print(f"  [summarize] LLM API error {resp.status_code}: {resp.text[:200]}")
            return None

        content = resp.json()["choices"][0]["message"]["content"]
        return _parse_json_response(content)

    except Exception as e:
        print(f"  [summarize] LLM call failed: {e}")
        return None


def _parse_json_response(text: str) -> dict | None:
    """Extract JSON from LLM response, handling markdown code blocks."""
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from ```json ... ``` block
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try finding any JSON object in the text
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    print(f"  [summarize] Could not parse JSON from: {text[:200]}")
    return None
