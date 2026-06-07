from collections import defaultdict
from config import MIN_TOTAL_STARS, TOP_PER_LANGUAGE, TOP_OVERALL, EXCLUDE_KEYWORDS, LANG_DISPLAY


def is_excluded(repo: dict) -> bool:
    name = (repo.get("fullname", "") + " " + repo.get("description", "")).lower()
    for kw in EXCLUDE_KEYWORDS:
        if kw in name:
            return True
    return False


def classify(repos_by_lang: dict[str, list[dict]]) -> dict:
    by_language: dict[str, list[dict]] = defaultdict(list)
    seen: set[str] = set()

    for lang_tag, repos in repos_by_lang.items():
        for repo in repos:
            fullname = repo.get("fullname", "")
            if fullname in seen:
                continue
            if repo.get("stars", 0) < MIN_TOTAL_STARS:
                continue
            if is_excluded(repo):
                continue
            seen.add(fullname)
            by_language[lang_tag].append(repo)

    for lang_tag in by_language:
        by_language[lang_tag].sort(key=lambda r: r.get("added_stars", 0), reverse=True)
        by_language[lang_tag] = by_language[lang_tag][:TOP_PER_LANGUAGE]

    all_repos = []
    seen_overall = set()
    for repos in by_language.values():
        for repo in repos:
            fn = repo.get("fullname", "")
            if fn not in seen_overall:
                seen_overall.add(fn)
                all_repos.append(repo)
    all_repos.sort(key=lambda r: r.get("added_stars", 0), reverse=True)

    return {
        "by_language": dict(by_language),
        "top_overall": all_repos[:TOP_OVERALL],
        "total_repos": sum(len(v) for v in by_language.values()),
    }


def format_repo_html(repo: dict, idx: int = 0) -> str:
    fullname = repo.get("fullname", "")
    stars = repo.get("stars", 0)
    added = repo.get("added_stars", 0)
    lang = repo.get("language", "")
    url = f"https://github.com/{fullname}"

    desc = repo.get("desc_cn", "") or repo.get("description", "") or ""
    desc = desc.strip().replace("\n", " ")

    num = f'{idx}.' if idx else ''
    return f'''<tr>
<td style="vertical-align:top;padding:10px 0;border-bottom:1px solid #eee">
  <a href="{url}" style="font-weight:bold;font-size:15px;text-decoration:none;color:#0366d6">{num} {fullname}</a>
  <p style="margin:4px 0;color:#333;font-size:13px">{desc}</p>
  <span style="font-size:12px;color:#586069">
    ⭐{stars:,} &nbsp; +{added:,} today &nbsp; {lang}
  </span>
</td>
</tr>'''


def format_lang_header(lang_tag: str) -> str:
    emoji, name = LANG_DISPLAY.get(lang_tag, ("", lang_tag or "Other"))
    return f'{emoji} {name}'
