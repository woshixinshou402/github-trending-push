"""GitHub Trending Daily Push — AI-enriched, HTML email to QQ Mail."""

import sys
import json
import os
from datetime import datetime, timezone, timedelta

from fetcher import fetch_all, normalize_repo
from classifier import classify, format_repo_html, format_lang_header
from enricher import enrich_descriptions
from pusher import send_email
from config import TOP_OVERALL, TRENDING_PERIOD, DEBUG

TZ_BEIJING = timezone(timedelta(hours=8))


def collect_all(classified: dict) -> list[dict]:
    seen = set()
    result = []
    for repo in classified.get("top_overall", []):
        n = repo.get("fullname", "")
        if n not in seen:
            seen.add(n)
            result.append(repo)
    for repos in classified.get("by_language", {}).values():
        for repo in repos:
            n = repo.get("fullname", "")
            if n not in seen:
                seen.add(n)
                result.append(repo)
    return result


CSS = """
body{font-family:Arial,Helvetica,sans-serif;max-width:680px;margin:0 auto;padding:20px;color:#24292e}
h1{font-size:20px;border-bottom:2px solid #0366d6;padding-bottom:8px}
h2{font-size:16px;margin-top:24px;color:#0366d6}
h3{font-size:14px;margin:16px 0 8px}
table{width:100%;border-collapse:collapse}
a{color:#0366d6;text-decoration:none}
a:hover{text-decoration:underline}
.footer{text-align:center;color:#586069;font-size:12px;margin-top:32px;padding-top:16px;border-top:1px solid #eee}
.stat{background:#f1f8ff;padding:4px 8px;border-radius:4px;font-size:12px;color:#0366d6}
"""


def build_html(classified: dict, date_str: str) -> str:
    parts = [f'<html><head><meta charset="utf-8"><style>{CSS}</style></head><body>']
    parts.append(f'<h1>GitHub Trending {date_str[:10]}</h1>')
    parts.append(f'<span class="stat">{classified["total_repos"]} repos · daily</span>')

    # TOP list
    parts.append('<h2>🏆 TOP 40</h2>')
    parts.append('<table>')
    for i, repo in enumerate(classified["top_overall"], 1):
        parts.append(format_repo_html(repo, idx=i))
    parts.append('</table>')

    # By language
    by_lang = classified.get("by_language", {})
    lang_order = sorted(
        by_lang.items(),
        key=lambda kv: sum(r.get("added_stars", 0) for r in kv[1]),
        reverse=True,
    )

    parts.append('<h2>📋 按语言分类</h2>')
    for lang_tag, repos in lang_order:
        if not repos or lang_tag == "":
            continue
        h = format_lang_header(lang_tag)
        parts.append(f'<h3>{h}</h3>')
        parts.append('<table>')
        for repo in repos:
            parts.append(format_repo_html(repo))
        parts.append('</table>')

    parts.append(f'<div class="footer">每日自动推送 · github.com/trending</div>')
    parts.append('</body></html>')
    return '\n'.join(parts)


def save_history(classified: dict, filepath: str = "data/history.json"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    today = datetime.now(TZ_BEIJING).strftime("%Y-%m-%d")
    history = {}
    if os.path.exists(filepath):
        try:
            history = json.loads(open(filepath, encoding="utf-8").read())
        except (json.JSONDecodeError, IOError):
            pass
    history = {k: v for k, v in history.items()
               if k >= (datetime.now(TZ_BEIJING) - timedelta(days=30)).strftime("%Y-%m-%d")}
    names = []
    for repos in classified.get("by_language", {}).values():
        for r in repos:
            names.append(r.get("fullname", ""))
    history[today] = names
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def main():
    print("=" * 50)
    print("GitHub Trending Daily Push")
    print("=" * 50)

    print("\n[1/3] Fetching...")
    raw = fetch_all(since=TRENDING_PERIOD)
    normalized: dict[str, list[dict]] = {}
    for lang_tag, repos in raw.items():
        normalized[lang_tag] = [normalize_repo(r, lang_tag) for r in repos]

    print("\n[2/3] Filtering & enriching...")
    classified = classify(normalized)
    all_repos = collect_all(classified)
    print(f"  {classified['total_repos']} repos filtered, {len(all_repos)} to enrich")

    cn_map = enrich_descriptions(all_repos)
    for repo in all_repos:
        name = repo.get("fullname", "")
        if name in cn_map:
            repo["desc_cn"] = cn_map[name]
    print(f"  {len(cn_map)} descriptions enriched")

    print("\n[3/3] Sending email...")
    date_str = datetime.now(TZ_BEIJING).strftime("%Y-%m-%d")
    html = build_html(classified, date_str)
    subject = f"GitHub Trending {date_str[:10]}"

    success = send_email(subject, html)
    if success:
        print("\n  Done! Check your QQ Mail.")
    else:
        print("\n  Email failed.", file=sys.stderr)
        sys.exit(1)

    save_history(classified)


if __name__ == "__main__":
    main()
