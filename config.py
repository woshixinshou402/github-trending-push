import os

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

LANG_DISPLAY = {
    "":            ("", "全语言"),
    "python":      ("", "Python"),
    "javascript":  ("", "JavaScript"),
    "typescript":  ("", "TypeScript"),
    "go":          ("", "Go"),
    "rust":        ("", "Rust"),
    "java":        ("", "Java"),
    "c":           ("", "C"),
    "c++":         ("", "C++"),
    "c#":          ("", "C#"),
    "swift":       ("", "Swift"),
    "kotlin":      ("", "Kotlin"),
    "ruby":        ("", "Ruby"),
    "php":         ("", "PHP"),
    "vue":         ("", "Vue"),
    "html":        ("", "HTML"),
    "css":         ("", "CSS"),
    "shell":       ("", "Shell"),
    "jupyter-notebook": ("", "Jupyter Notebook"),
    "dart":        ("", "Dart"),
    "scala":       ("", "Scala"),
}

MIN_TOTAL_STARS = 100
TOP_PER_LANGUAGE = 8
TOP_OVERALL = 40
TRENDING_PERIOD = "daily"

EXCLUDE_KEYWORDS = [
    "security", "vulnerability", "exploit", "pentest", "penetration",
    "hack", "malware", "phishing", "cve-", "backdoor", "ransomware",
    "fuzzer", "fuzzing", "payload", "shellcode", "rootkit", "keylogger",
    "reverse-engineering", "reversing", "xss", "csrf", "sqli",
    "redteam", "red-team", "blueteam", "blue-team", "cyber",
    "cracking", "crack", "bypass", "spoof", "trojan", "virus",
    "osint", "steganography", "forensic",
]

WXPUSHER_APP_TOKEN = os.environ.get("WXPUSHER_APP_TOKEN", "")
WXPUSHER_UID = os.environ.get("WXPUSHER_UID", "")

LLM_API_KEY = os.environ.get("LLM_API_KEY") or ""
LLM_API_BASE = os.environ.get("LLM_API_BASE") or "https://token-plan-cn.xiaomimimo.com/v1"
LLM_MODEL = os.environ.get("LLM_MODEL") or "mimo-v2.5-pro"

DEBUG = os.environ.get("DEBUG", "").lower() == "true"
