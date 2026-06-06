"""AI-powered description enricher: rewrites repo descriptions in clear Chinese."""

import json
import re
import requests
from config import LLM_API_KEY, LLM_API_BASE, LLM_MODEL, DEBUG

SYSTEM_PROMPT = """你是一个技术编辑。对于每个 GitHub 仓库，用一句简短的中文（30字以内）说明它是什么、能做什么。

输入格式（JSON 数组）：
[{"name": "owner/repo", "desc": "原始英文描述", "lang": "Python"}]

输出格式（只输出 JSON，不要其他内容）：
[{"name": "owner/repo", "desc_cn": "中文一句话简介"}]

规则：
- 描述要具体，不要说"一个工具"、"一个框架"，要说清楚具体功能
- 如果原始描述看不懂或太泛，根据仓库名推测用途
- 不要翻译腔，用自然的中文表达"""


def enrich_descriptions(repos: list[dict]) -> dict[str, str]:
    """Given a list of repo dicts, return a mapping of fullname -> Chinese description.

    Returns empty dict if LLM is not configured or fails.
    """
    if not LLM_API_KEY:
        if DEBUG:
            print("  [enricher] No LLM_API_KEY, skipping")
        return {}

    # Build input list
    items = []
    for repo in repos:
        items.append({
            "name": repo.get("fullname", ""),
            "desc": repo.get("description", ""),
            "lang": repo.get("language", ""),
        })

    if not items:
        return {}

    if DEBUG:
        print(f"  [enricher] Enriching {len(items)} descriptions...")

    # Split into batches of 30 to avoid token limits
    results = {}
    batch_size = 30
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        try:
            batch_results = _call_llm(batch)
            for item in batch_results:
                name = item.get("name", "")
                desc_cn = item.get("desc_cn", "")
                if name and desc_cn:
                    results[name] = desc_cn
        except Exception as e:
            print(f"  [enricher] Batch {i // batch_size} failed: {e}")
            continue

    if DEBUG:
        print(f"  [enricher] Got {len(results)} enriched descriptions")

    return results


def _call_llm(items: list[dict]) -> list[dict]:
    """Call LLM to enrich a batch of descriptions."""
    if not LLM_API_KEY:
        return []

    body = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(items, ensure_ascii=False)},
        ],
        "temperature": 0.3,
        "max_tokens": 2000,
    }

    resp = requests.post(
        f"{LLM_API_BASE}/chat/completions",
        headers={
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=120,
    )

    if resp.status_code != 200:
        print(f"  [enricher] LLM error {resp.status_code}: {resp.text[:300]}")
        return []

    content = resp.json()["choices"][0]["message"]["content"]
    return _parse_json(content)


def _parse_json(text: str) -> list[dict]:
    """Extract JSON array from LLM response."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    match = re.search(r"\[[\s\S]*\]", text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    print(f"  [enricher] JSON parse failed: {text[:200]}")
    return []
