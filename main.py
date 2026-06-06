"""GitHub Trending Daily Push — fetch trending repos by language, enrich with AI, and push to WeChat."""

import sys
import json
import os
from datetime import datetime, timezone, timedelta

from fetcher import fetch_all, normalize_repo
from classifier import classify, format_repo_card, format_lang_header
from enricher import enrich_descriptions
from summarizer import summarize
from pusher import send_daily_report
from config import TOP_OVERALL, TOP_PER_LANGUAGE, TRENDING_PERIOD, DEBUG

TZ_BEIJING = timezone(timedelta(hours=8))


def inject_cn_descriptions(classified: dict, cn_map: dict[str, str]):
    """Inject enriched Chinese descriptions into repo dicts."""
    for repos in classified.get("by_language", {}).values():
        for repo in repos:
            name = repo.get("fullname", "")
            if name in cn_map:
                repo["desc_cn"] = cn_map[name]
    for repo in classified.get("top_overall", []):
        name = repo.get("fullname", "")
        if name in cn_map:
            repo["desc_cn"] = cn_map[name]


def collect_all_repos(classified: dict) -> list[dict]:
    """Collect all unique repos from classified data."""
    seen = set()
    result = []
    for repos in classified.get("by_language", {}).values():
        for repo in repos:
            name = repo.get("fullname", "")
            if name not in seen:
                seen.add(name)
                result.append(repo)
    return result


def build_report(classified: dict, date_str: str) -> str:
    """Build the daily report in clean Markdown format."""
    lines = []

    lines.append(f"# GitHub Trending {date_str[:10]}")
    lines.append("")

    # Top 10 overall
    top = classified["top_overall"]
    if top:
        lines.append(f"##  全语言 TOP {len(top)}")
        lines.append("")
        for i, repo in enumerate(top, 1):
            lines.append(f"**{i}. {format_repo_card(repo)}**")
            lines.append("")

    # By language
    by_lang = classified.get("by_language", {})
    lang_order = sorted(
        by_lang.items(),
        key=lambda kv: sum(r.get("added_stars", 0) for r in kv[1]),
        reverse=True,
    )

    if lang_order:
        lines.append("---")
        lines.append("##  按语言分类")
        lines.append("")

    for lang_tag, repos in lang_order:
        if not repos or lang_tag == "":
            continue
        header = format_lang_header(lang_tag)
        lines.append(f"### {header}")
        lines.append("")
        for repo in repos:
            lines.append(format_repo_card(repo))
            lines.append("")

    k = classified["total_repos"]
    lines.append("---")
    lines.append(f"*{k} 个仓库  •  每日自动推送  •  github.com/trending*")

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

    history = {k: v for k, v in history.items() if k >= _days_ago(30)}

    names = []
    for repos in classified.get("by_language", {}).values():
        for r in repos:
            names.append(r.get("fullname", ""))

    history[today] = names
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def _days_ago(n: int) -> str:
    return (datetime.now(TZ_BEIJING) - timedelta(days=n)).strftime("%Y-%m-%d")


def main():
    print("=" * 50)
    print("GitHub Trending Daily Push")
    print("=" * 50)

    # 1. Fetch
    print("\n[1/5] Fetching trending repos...")
    raw = fetch_all(since=TRENDING_PERIOD)
    normalized: dict[str, list[dict]] = {}
    for lang_tag, repos in raw.items():
        normalized[lang_tag] = [normalize_repo(r, lang_tag) for r in repos]

    # 2. Classify
    print("\n[2/5] Classifying by language...")
    classified = classify(normalized)
    print(f"  {classified['total_repos']} repos after filtering")

    # 3. Enrich with Chinese descriptions
    print("\n[3/5] AI enriching descriptions...")
    all_repos = collect_all_repos(classified)
    cn_map = enrich_descriptions(all_repos)
    inject_cn_descriptions(classified, cn_map)
    print(f"  {len(cn_map)} descriptions enriched")

    # 4. AI Summary
    print("\n[4/5] Generating AI summary...")
    ai_result = summarize(classified)
    if ai_result:
        print(f"  Summary: {ai_result.get('summary', '')[:100]}...")
    else:
        print("  Skipped")

    # 5. Build report and push
    print("\n[5/5] Building report and pushing to WeChat...")
    date_str = datetime.now(TZ_BEIJING).strftime("%Y-%m-%d %A")
    report = build_report(classified, date_str)

    if DEBUG:
        print(f"\n--- Report Preview ({len(report)} chars) ---")
        try:
            print(report[:3000])
        except UnicodeEncodeError:
            print(report[:3000].encode("utf-8", errors="replace")
                  .decode("utf-8", errors="replace"))
        print("...")

    success = send_daily_report(report)
    if success:
        print("\n  Done! Report pushed to WeChat.")
    else:
        print("\n  Push failed.", file=sys.stderr)
        sys.exit(1)

    save_history(classified)
    print("  History saved.")


if __name__ == "__main__":
    main()
