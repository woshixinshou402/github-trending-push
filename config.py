import os

# Only track these languages
LANGUAGES = [
    "python",
    "c++",
]

LANG_DISPLAY = {
    "python":      ("Python", "python"),
    "c++":         ("C++", "c++"),
}

# Minimum added stars today to include
MIN_ADDED_STARS = 500

# Number of repos in the daily push
TOP_OVERALL = 40

# Trending period: "daily" or "weekly"
TRENDING_PERIOD = "daily"

# Filter out repos with these keywords in name/description (case-insensitive)
EXCLUDE_KEYWORDS = [
    "security", "vulnerability", "exploit", "pentest", "penetration",
    "hack", "malware", "phishing", "cve-", "backdoor", "ransomware",
    "fuzzer", "fuzzing", "payload", "shellcode", "rootkit", "keylogger",
    "reverse-engineering", "reversing", "xss", "csrf", "sqli",
    "redteam", "red-team", "blueteam", "blue-team", "cyber",
    "cracking", "crack", "bypass", "spoof", "trojan", "virus",
    "osint", "steganography", "forensic",
]

# WxPusher configuration
WXPUSHER_APP_TOKEN = os.environ.get("WXPUSHER_APP_TOKEN", "")
WXPUSHER_UID = os.environ.get("WXPUSHER_UID", "")

# LLM configuration
LLM_API_KEY = os.environ.get("LLM_API_KEY") or ""
LLM_API_BASE = os.environ.get("LLM_API_BASE") or "https://token-plan-cn.xiaomimimo.com/v1"
LLM_MODEL = os.environ.get("LLM_MODEL") or "mimo-v2.5-pro"

DEBUG = os.environ.get("DEBUG", "").lower() == "true"
