from concurrent.futures import ThreadPoolExecutor, as_completed
from gtrending import fetch_repos
from config import LANGUAGES, TRENDING_PERIOD, DEBUG


def fetch_single(language: str, since: str = "daily") -> list[dict]:
    """Fetch trending repos for a single language."""
    lang_display = language or "all"
    try:
        repos = fetch_repos(language=language or None, since=since)
        if DEBUG:
            print(f"  [fetch] {lang_display}: got {len(repos)} repos")
        return repos
    except Exception as e:
        print(f"  [fetch] ERROR {lang_display}: {e}")
        return []


def fetch_all(since: str = None) -> dict[str, list[dict]]:
    """Fetch trending repos for all configured languages in parallel.

    Returns a dict mapping language slug -> list of repo dicts.
    """
    period = since or TRENDING_PERIOD
    results: dict[str, list[dict]] = {}

    print(f"Fetching trending repos for {len(LANGUAGES)} languages (period={period})...")

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(fetch_single, lang, period): lang
            for lang in LANGUAGES
        }
        for future in as_completed(futures):
            lang = futures[future]
            repos = future.result()
            if repos:
                results[lang] = repos

    total = sum(len(v) for v in results.values())
    print(f"Fetched {total} repos across {len(results)} languages")
    return results


def normalize_repo(repo: dict, language_tag: str = "") -> dict:
    """Normalize a repo dict from gtrending to our internal format."""
    return {
        "fullname": repo.get("fullname", repo.get("name", "")),
        "name": repo.get("name", repo.get("fullname", "").split("/")[-1]
                         if "/" in repo.get("fullname", "") else repo.get("fullname", "")),
        "description": (repo.get("description") or "").strip(),
        "language": repo.get("language") or language_tag or "Unknown",
        "stars": int(repo.get("stars", 0)),
        "forks": int(repo.get("forks", 0)),
        "added_stars": int(repo.get("added_stars", repo.get("currentPeriodStars", 0))),
        "url": repo.get("url", f"https://github.com/{repo.get('fullname', '')}"),
        "built_by": repo.get("builtBy", repo.get("built_by", [])),
    }
