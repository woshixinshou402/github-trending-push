from config import MIN_ADDED_STARS, TOP_OVERALL, EXCLUDE_KEYWORDS


def is_excluded(repo: dict) -> bool:
    """Check if repo should be excluded (security keywords)."""
    name = (repo.get("fullname", "") + " " + repo.get("description", "")).lower()
    for kw in EXCLUDE_KEYWORDS:
        if kw in name:
            return True
    return False


def classify(repos_by_lang: dict[str, list[dict]]) -> dict:
    """Filter by added stars, exclude security, sort by added stars desc.

    Returns:
        "repos": flat list of top repos
        "total_repos": count after filtering
    """
    seen: set[str] = set()
    filtered: list[dict] = []

    for lang_tag, repos in repos_by_lang.items():
        for repo in repos:
            fullname = repo.get("fullname", "")
            if fullname in seen:
                continue
            seen.add(fullname)

            # Filter by added stars
            added = repo.get("added_stars", 0)
            if added < MIN_ADDED_STARS:
                continue

            # Filter out security
            if is_excluded(repo):
                continue

            filtered.append(repo)

    # Sort by added stars descending
    filtered.sort(key=lambda r: r.get("added_stars", 0), reverse=True)

    return {
        "repos": filtered[:TOP_OVERALL],
        "total_repos": len(filtered),
    }


def format_repo_card(repo: dict, idx: int = 0) -> str:
    """Format a repo with number, name, Chinese description, stats."""
    fullname = repo.get("fullname", "")
    stars = repo.get("stars", 0)
    added = repo.get("added_stars", 0)
    lang = repo.get("language", "")
    url = repo.get("url", f"https://github.com/{fullname}")

    desc = repo.get("desc_cn", "") or repo.get("description", "") or ""
    desc = desc.strip().replace("\n", " ")
    if len(desc) > 100:
        desc = desc[:100] + "..."

    num = f"{idx}." if idx else ""
    return (
        f"**{num} {fullname}**\n"
        f"  {desc}\n"
        f"  ⭐{stars:,} · +{added:,} today · {lang or 'Unknown'} · {url}"
    )
