"""AI-powered description enricher: rewrites repo descriptions in clear Chinese."""

import json
import re
import requests
from config import LLM_API_KEY, LLM_API_BASE, LLM_MODEL, DEBUG

SYSTEM_PROMPT = """你是一个技术编辑。对每个 GitHub 仓库，用一句简洁中文（25字内）说明它是什么能做什么。

输入：每行一个仓库，格式: owner/repo | 语言 | 英文描述
输出：每行一个仓库，格式: owner/repo | 中文简介

直接输出，不要任何解释。例如：
输入: mvanhorn/ai-skill | Python | AI agent skill for research
输出: mvanhorn/ai-skill | 跨平台AI研究技能，集成多数据源"""


def enrich_descriptions(repos: list[dict]) -> dict[str, str]:
    if not LLM_API_KEY:
        return {}

    if not repos:
        return {}

    # Build input text
    lines = []
    for repo in repos:
        name = repo.get("fullname", "")
        lang = repo.get("language", "")
        desc = (repo.get("description") or "").strip().replace("\n", " ")
        if not desc:
            desc = "(no description)"
        lines.append(f"{name} | {lang} | {desc}")

    if DEBUG:
        print(f"  [enricher] Enriching {len(repos)} descriptions...")

    results = {}
    batch_size = 15

    for i in range(0, len(lines), batch_size):
        batch = lines[i:i + batch_size]
        batch_text = "\n".join(batch)
        try:
            batch_results = _call_llm(batch_text)
            for name, desc_cn in batch_results.items():
                if desc_cn and desc_cn.strip():
                    results[name] = desc_cn.strip()
        except Exception as e:
            print(f"  [enricher] Batch {i // batch_size} error: {e}")

    if DEBUG:
        print(f"  [enricher] Enriched {len(results)}/{len(repos)} descriptions")

    return results


def _call_llm(lines_text: str) -> dict[str, str]:
    body = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": lines_text},
        ],
        "temperature": 0.2,
        "max_tokens": 3000,
    }

    resp = requests.post(
        f"{LLM_API_BASE}/chat/completions",
        headers={
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=180,
    )

    if resp.status_code != 200:
        print(f"  [enricher] HTTP {resp.status_code}: {resp.text[:300]}")
        return {}

    content = resp.json()["choices"][0]["message"]["content"]
    if DEBUG:
        print(f"  [enricher] Response length: {len(content)} chars")

    return _parse_lines(content)


def _parse_lines(text: str) -> dict[str, str]:
    """Parse LLM output: each line is 'owner/repo | 中文简介'"""
    results = {}
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line or "|" not in line:
            continue
        # Remove markdown markers
        line = re.sub(r'^[\s\-*>#*]+', '', line).strip()

        parts = line.split("|", 1)
        if len(parts) == 2:
            name = parts[0].strip()
            desc = parts[1].strip()
            if "/" in name and desc:
                results[name] = desc

    return results
