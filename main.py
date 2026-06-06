"""GitHub Trending Daily Push — Python & C++, AI-enriched, pushed to WeChat."""

import sys
import json
import os
from datetime import datetime, timezone, timedelta

from fetcher import fetch_all, normalize_repo
from classifier import classify, format_repo_card
from enricher import enrich_descriptions
from pusher import send_daily_report
from config import TOP_OVERALL, TRENDING_PERIOD, DEBUG

TZ_BEIJING = timezone(timedelta(hours=8))


def build_report(repos: list[dict], date_str: str) -> str:
    """Build clean daily report with AI-enriched descriptions."""
    lines = []

    lines.append(f"# GitHub Trending {date_str[:10]}")
    lines.append(f"{len(repos)} 个项目 · Python & C++ · 新增 >500 star")
    lines.append("")

    for i, repo in enumerate(repos, 1):
        lines.append(format_repo_card(repo, idx=i))
        lines.append("")

    lines.append("---")
    lines.append(f"*每日自动推送 · github.com/trending*")

    return "\n".join(lines)


def save_history(repos: list[dict], filepath: str = "data/history.json"):
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

    history[today] = [r.get("fullname", "") for r in repos]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def main():
    print("=" * 50)
    print("GitHub Trending Daily Push")
    print("=" * 50)

    # 1. Fetch
    print("\n[1/4] Fetching Python & C++ trending...")
    raw = fetch_all(since=TRENDING_PERIOD)
    normalized: dict[str, list[dict]] = {}
    for lang_tag, repos in raw.items():
        normalized[lang_tag] = [normalize_repo(r, lang_tag) for r in repos]

    # 2. Classify & filter
    print("\n[2/4] Filtering (>500 stars today, no security)...")
    classified = classify(normalized)
    repos = classified["repos"]
    print(f"  {classified['total_repos']} repos matched, top {len(repos)} selected")

    if not repos:
        print("  No repos matched today. Check thresholds in config.py.")
        return

    # 3. AI enrich descriptions
    print("\n[3/4] AI enriching descriptions...")
    cn_map = enrich_descriptions(repos)
    for repo in repos:
        name = repo.get("fullname", "")
        if name in cn_map:
            repo["desc_cn"] = cn_map[name]
    print(f"  {len(cn_map)} descriptions enriched")

    # 4. Build report and push
    print("\n[4/4] Building report and pushing...")
    date_str = datetime.now(TZ_BEIJING).strftime("%Y-%m-%d")
    report = build_report(repos, date_str)

    if DEBUG:
        print(f"\n--- Report Preview ({len(report)} chars) ---")
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

    save_history(repos)
    print("  History saved.")


if __name__ == "__main__":
    main()
