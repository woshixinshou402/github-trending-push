"""GitHub Trending Daily Push — AI-enriched descriptions, pushed to WeChat."""

import sys
import json
import os
from datetime import datetime, timezone, timedelta

from fetcher import fetch_all, normalize_repo
from classifier import classify, format_repo_card, format_lang_header
from enricher import enrich_descriptions
from pusher import send_daily_report
from config import TOP_OVERALL, TOP_PER_LANGUAGE, TRENDING_PERIOD, DEBUG

TZ_BEIJING = timezone(timedelta(hours=8))


def collect_all_repos(classified: dict) -> list[dict]:
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


def build_report(classified: dict, date_str: str) -> str:
    lines = []

    lines.append(f"GitHub Trending  {date_str[:10]}")
    lines.append("")

    top = classified["top_overall"]
    if top:
        lines.append(f"=== TOP {len(top)} ===")
        lines.append("")
        for i, repo in enumerate(top, 1):
            lines.append(format_repo_card(repo, idx=i))
            lines.append("")

    by_lang = classified.get("by_language", {})
    lang_order = sorted(
        by_lang.items(),
        key=lambda kv: sum(r.get("added_stars", 0) for r in kv[1]),
        reverse=True,
    )

    if lang_order:
        lines.append("==========")
        lines.append("")

    for lang_tag, repos in lang_order:
        if not repos or lang_tag == "":
            continue
        h = format_lang_header(lang_tag)
        lines.append(f"-- {h} --")
        lines.append("")
        for repo in repos:
            lines.append(format_repo_card(repo))
            lines.append("")

    k = classified["total_repos"]
    lines.append("==========")
    lines.append(f"{k} repos  github.com/trending")

    return "\n".join(lines)


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

    print("\n[1/4] Fetching...")
    raw = fetch_all(since=TRENDING_PERIOD)
    normalized: dict[str, list[dict]] = {}
    for lang_tag, repos in raw.items():
        normalized[lang_tag] = [normalize_repo(r, lang_tag) for r in repos]

    print("\n[2/4] Filtering...")
    classified = classify(normalized)
    print(f"  {classified['total_repos']} repos after filtering")

    all_repos = collect_all_repos(classified)
    print(f"  {len(all_repos)} unique repos to enrich")

    print("\n[3/4] AI enriching descriptions...")
    cn_map = enrich_descriptions(all_repos)
    for repo in all_repos:
        name = repo.get("fullname", "")
        if name in cn_map:
            repo["desc_cn"] = cn_map[name]
    print(f"  {len(cn_map)} enriched")

    print("\n[4/4] Pushing...")
    date_str = datetime.now(TZ_BEIJING).strftime("%Y-%m-%d")
    report = build_report(classified, date_str)

    if DEBUG:
        print(f"\n--- Preview ({len(report)} chars) ---")
        try:
            print(report[:3000])
        except UnicodeEncodeError:
            pass
        print("...")

    success = send_daily_report(report)
    if success:
        print("\n  Done!")
    else:
        print("\n  Push failed.", file=sys.stderr)
        sys.exit(1)

    save_history(classified)
    print("  History saved.")


if __name__ == "__main__":
    main()
