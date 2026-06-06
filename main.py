"""GitHub Trending Daily Push — fetch trending repos by language, summarize with AI, and push to WeChat."""

import sys
import json
import os
from datetime import datetime, timezone, timedelta

from fetcher import fetch_all, normalize_repo
from classifier import classify, format_repo_line, format_lang_header
from summarizer import summarize
from pusher import send_daily_report
from config import TOP_OVERALL, TOP_PER_LANGUAGE, TRENDING_PERIOD, DEBUG

# Beijing timezone
TZ_BEIJING = timezone(timedelta(hours=8))


def build_report(classified: dict, ai_result: dict | None, date_str: str) -> str:
    """Build the full HTML report string from classified data and AI summary."""
    lines = []

    # Header
    lines.append(f"<h2>GitHub Trending 日报 | {date_str}</h2>")

    # AI Summary section
    if ai_result:
        lines.append("<h3> 今日总览</h3>")
        summary_text = ai_result.get("summary", "")
        if summary_text:
            lines.append(f"<blockquote>{summary_text}</blockquote>")

        highlights = ai_result.get("highlights", [])
        if highlights:
            lines.append("<p><b> 精选推荐：</b></p>")
            for h in highlights:
                name = h.get("name", "")
                reason = h.get("reason", "")
                lines.append(f"  <b>{name}</b> — {reason}")

    # Top overall
    lines.append("<h3> 全语言 TOP {}</h3>".format(len(classified["top_overall"])))
    for i, repo in enumerate(classified["top_overall"], 1):
        lines.append(f"{i}. {format_repo_line(repo)}")

    # By language
    lines.append("<h3> 按语言分类</h3>")
    by_lang = classified.get("by_language", {})
    # Sort languages by total added_stars in each group
    lang_order = sorted(
        by_lang.items(),
        key=lambda kv: sum(r.get("added_stars", 0) for r in kv[1]),
        reverse=True,
    )

    for lang_tag, repos in lang_order:
        if not repos:
            continue
        header = format_lang_header(lang_tag)
        lines.append(f"<p><b>{header}</b></p>")
        for i, repo in enumerate(repos, 1):
            lines.append(f"  {i}. {format_repo_line(repo, show_lang=False)}")

    # Footer
    lines.append("<hr>")
    lines.append(
        "<small>数据来源: github.com/trending | "
        f"共收录 {classified['total_repos']} 个仓库 | "
        f"每日 {date_str[:5]} 自动推送</small>"
    )

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
