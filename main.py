"""GitHub Trending Daily Push — fetch trending repos by language, summarize with AI, and push to WeChat."""

import sys
import json
import os
from datetime import datetime, timezone, timedelta

from fetcher import fetch_all, normalize_repo
from classifier import classify, format_repo_card, format_lang_header
from summarizer import summarize
from pusher import send_daily_report
from config import TOP_OVERALL, TOP_PER_LANGUAGE, TRENDING_PERIOD, DEBUG

# Beijing timezone
TZ_BEIJING = timezone(timedelta(hours=8))


def build_report(classified: dict, ai_result: dict | None, date_str: str) -> str:
    """Build the daily report in clean Markdown format."""
    lines = []

    lines.append(f"# GitHub Trending {date_str[:10]}")
    lines.append("")

    # AI Summary
    if ai_result:
        summary_text = ai_result.get("summary", "")
        if summary_text:
            lines.append(f"###  今日趋势")
            lines.append(f"> {summary_text}")
            lines.append("")

        highlights = ai_result.get("highlights", [])
        if highlights:
            lines.append("###  值得关注")
            for h in highlights:
                name = h.get("name", "")
                reason = h.get("reason", "")
                lines.append(f"- **{name}**：{reason}")
            lines.append("")

    # Top 10 overall
    top = classified["top_overall"]
    if top:
        lines.append(f"---")
        lines.append(f"##  全语言 TOP {len(top)}")
        lines.append("")
        for i, repo in enumerate(top, 1):
            lines.append(format_repo_card(repo))
            lines.append("")

    # By language
    by_lang = classified.get("by_language", {})
    # Sort by total added_stars in each group
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
        if not repos or lang_tag == "":  # skip "all languages" in per-lang section
            continue
        header = format_lang_header(lang_tag)
        lines.append(f"### {header}")
        lines.append("")
        for repo in repos:
            lines.append(format_repo_card(repo, for_lang_section=True))
            lines.append("")

    # Footer
    k = classified["total_repos"]
    lines.append("---")
    lines.append(f"*{k} 个仓库  •  每日自动推送  •  github.com/trending*")

    return "\n".join(lines)


def save_history(classified: dict, filepath: str = "data/history.json"):
    """Save today's repo names to history for dedup."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    today = datetime.now(TZ_BEIJING).strftime("%Y-%m-%d")
    history = {}
    if os.path.exists(filepath):
        try:
            history = json.loads(open(filepath, encoding="utf-8").read())
        except (json.JSONDecodeError, IOError):
            pass

    # Keep only last 30 days
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
    print("\n[1/4] Fetching trending repos...")
    raw = fetch_all(since=TRENDING_PERIOD)

    # Normalize all repos
    normalized: dict[str, list[dict]] = {}
    for lang_tag, repos in raw.items():
        normalized[lang_tag] = [normalize_repo(r, lang_tag) for r in repos]

    # 2. Classify
    print("\n[2/4] Classifying by language...")
    classified = classify(normalized)
    print(f"  {classified['total_repos']} repos after filtering "
          f"(top {TOP_PER_LANGUAGE} per language, top {TOP_OVERALL} overall)")

    # 3. AI Summary (optional)
    print("\n[3/4] Generating AI summary...")
    ai_result = summarize(classified)
    if ai_result:
        print(f"  Summary: {ai_result.get('summary', '')[:100]}...")
    else:
        print("  Skipped (no LLM configured or API error)")

    # 4. Build report and push
    print("\n[4/4] Building report and pushing to WeChat...")
    date_str = datetime.now(TZ_BEIJING).strftime("%Y-%m-%d %A")
    report = build_report(classified, ai_result, date_str)

    if DEBUG:
        print(f"\n--- Report Preview ({len(report)} chars) ---")
        try:
            print(report[:2000])
        except UnicodeEncodeError:
            # Windows GBK terminal can't print emoji
            print(report[:2000].encode("utf-8", errors="replace").decode("utf-8", errors="replace"))
        print("...")

    success = send_daily_report(report)
    if success:
        print("\n  Done! Report pushed to WeChat.")
    else:
        print("\n  Push failed. Check WXPUSHER_SPT configuration.", file=sys.stderr)
        sys.exit(1)

    # Save history for dedup
    save_history(classified)
    print("  History saved.")


if __name__ == "__main__":
    main()
