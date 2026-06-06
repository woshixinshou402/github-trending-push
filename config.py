import os

# Languages to fetch trending repos for (empty string = all languages)
LANGUAGES = [
    "",             # all languages
    "python",
    "javascript",
    "typescript",
    "go",
    "rust",
    "java",
    "c",
    "c++",
    "c#",
    "swift",
    "kotlin",
    "ruby",
    "php",
    "vue",
    "html",
    "css",
    "shell",
    "jupyter-notebook",
    "dart",
    "scala",
]

# Language display names and emoji
LANG_DISPLAY = {
    "":            ("📊", "全语言"),
    "python":      ("🐍", "Python"),
    "javascript":  ("🟨", "JavaScript"),
    "typescript":  ("🔷", "TypeScript"),
    "go":          ("🔵", "Go"),
    "rust":        ("🦀", "Rust"),
    "java":        ("☕", "Java"),
    "c":           ("⚙️", "C"),
    "c++":         ("🔧", "C++"),
    "c#":          ("🟣", "C#"),
    "swift":       ("🍎", "Swift"),
    "kotlin":      ("💜", "Kotlin"),
    "ruby":        ("♦️", "Ruby"),
    "php":         ("🐘", "PHP"),
    "vue":         ("💚", "Vue"),
    "html":        ("🏷️", "HTML"),
    "css":         ("🎨", "CSS"),
    "shell":       ("🐚", "Shell"),
    "jupyter-notebook": ("📓", "Jupyter Notebook"),
    "dart":        ("🎯", "Dart"),
    "scala":       ("🔴", "Scala"),
    "zig":         ("⚡", "Zig"),  # not supported by gtrending yet, keep for reference
}

# Star threshold: only include repos with at least this many total stars
MIN_TOTAL_STARS = 100

# Number of top repos per language in the report
TOP_PER_LANGUAGE = 5

# Number of repos in the all-language top list
TOP_OVERALL = 10

# Trending period: "daily" or "weekly"
TRENDING_PERIOD = "daily"

# WxPusher configuration
WXPUSHER_APP_TOKEN = os.environ.get("WXPUSHER_APP_TOKEN", "")
WXPUSHER_UID = os.environ.get("WXPUSHER_UID", "")

# LLM configuration (optional, for AI summary)
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_API_BASE = os.environ.get("LLM_API_BASE", "https://api.openai.com/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")

# GitHub Actions outputs debug info
DEBUG = os.environ.get("DEBUG", "").lower() == "true"
