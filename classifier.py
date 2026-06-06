from collections import defaultdict
from config import MIN_TOTAL_STARS, TOP_PER_LANGUAGE, TOP_OVERALL, LANG_DISPLAY


def classify(repos_by_lang: dict[str, list[dict]]) -> dict:
    """Group repos by language, filter by star threshold, and sort.

    Returns a dict with:
        "by_language": {lang: [repos sorted by added_stars desc]}
        "top_overall": [top repos across all languages]
        "total_repos": total count after filtering
    """
    by_language: dict[str, list[dict]] = defaultdict(list)
    seen: set[str] = set()

    for lang_tag, repos in repos_by_lang.items():
        for repo in repos:
            fullname = repo.get("fullname", "")
            if fullname in seen:
                continue
            if repo.get("stars", 0) < MIN_TOTAL_STARS:
                continue
            seen.add(fullname)
            by_language[lang_tag].append(repo)

    # Sort each language group by added_stars descending
    for lang_tag in by_language:
        by_language[lang_tag].sort(key=lambda r: r.get("added_stars", 0), reverse=True)
        # Keep only top N per language
        by_language[lang_tag] = by_language[lang_tag][:TOP_PER_LANGUAGE]

    # Top overall: combine all, sort by added_stars, deduplicate
    all_repos = []
    seen_overall = set()
    for repos in by_language.values():
        for repo in repos:
            fn = repo.get("fullname", "")
            if fn not in seen_overall:
                seen_overall.add(fn)
                all_repos.append(repo)
    all_repos.sort(key=lambda r: r.get("added_stars", 0), reverse=True)
    top_overall = all_repos[:TOP_OVERALL]

    total = sum(len(v) for v in by_language.values())

    return {
        "by_language": dict(by_language),
        "top_overall": top_overall,
        "total_repos": total,
    }


def format_repo_card(repo: dict, for_lang_section: bool = False) -> str:
    """Format a repo as a readable card with clear description of what it does."""
    fullname = repo.get("fullname", "")
    stars = repo.get("stars", 0)
    added = repo.get("added_stars", 0)
    desc = repo.get("description", "") or ""
    url = repo.get("url", f"https://github.com/{fullname}")
    lang = repo.get("language", "")

    # Build clean description
    desc = desc.strip().replace("\n", " ")
    if not desc:
        desc = "(暂无描述)"
    # Ensure description ends with proper punctuation
    if len(desc) > 120:
        desc = desc[:120] + "..."

    lines = [
        f"**{fullname}**",
        f"> {desc}",
        f"⭐{stars:,}  •  +{added:,} today  •  [{lang or 'Unknown'}]({url})",
    ]
    return "\n".join(lines)


def format_lang_header(lang_tag: str) -> str:
    """Get emoji + display name for a language tag."""
    emoji, name = LANG_DISPLAY.get(lang_tag, ("📦", lang_tag or "Other"))
    return f"**{emoji} {name}**"
