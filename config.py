import os

LANGUAGES = [
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
    "jupyter-notebook",
    "dart",
    "scala",
]

LANG_DISPLAY = {
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
    "jupyter-notebook": ("📓", "Jupyter"),
    "dart":        ("🎯", "Dart"),
    "scala":       ("🔴", "Scala"),
}

MIN_TOTAL_STARS = 100
TOP_PER_LANGUAGE = 5
TOP_OVERALL = 40
TRENDING_PERIOD = "daily"

EXCLUDE_KEYWORDS = [
    "security", "vulnerability", "exploit", "pentest",
    "malware", "phishing", "cve-", "backdoor", "ransomware",
    "fuzzer", "payload", "shellcode", "rootkit",
    "redteam", "red-team", "blueteam", "blue-team", "cyber",
    "cracking", "bypass", "trojan", "virus",
    "osint", "steganography", "forensic",
]

# Email (QQ Mail SMTP)
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
TO_EMAIL = os.environ.get("TO_EMAIL", "")

# LLM
LLM_API_KEY = os.environ.get("LLM_API_KEY") or ""
LLM_API_BASE = os.environ.get("LLM_API_BASE") or "https://token-plan-cn.xiaomimimo.com/v1"
LLM_MODEL = os.environ.get("LLM_MODEL") or "mimo-v2.5-pro"

DEBUG = os.environ.get("DEBUG", "").lower() == "true"
