import requests
from config import WXPUSHER_APP_TOKEN, WXPUSHER_UID, DEBUG

WXPUSHER_API = "https://wxpusher.zjiecode.com/api/send/message"
MAX_CONTENT_LEN = 40000


def push_to_wechat(content: str) -> bool:
    """Push a message to WeChat via WxPusher (appToken + UID)."""
    if not WXPUSHER_APP_TOKEN or not WXPUSHER_UID:
        print("[push] ERROR: WXPUSHER_APP_TOKEN or WXPUSHER_UID not configured")
        return False

    if len(content) > MAX_CONTENT_LEN:
        content = content[:MAX_CONTENT_LEN - 100] + "\n\n... (内容过长已截断)"

    uids = [u.strip() for u in WXPUSHER_UID.split(",") if u.strip()]

    body = {
        "appToken": WXPUSHER_APP_TOKEN,
        "content": content,
        "contentType": 2,  # 2 = HTML
        "uids": uids,
    }

    try:
        resp = requests.post(WXPUSHER_API, json=body, timeout=30)
        data = resp.json()
        if DEBUG:
            print(f"  [push] Response: {data}")

        if data.get("code") == 1000:
            for item in data.get("data", []):
                if item.get("code") != 1000:
                    print(f"  [push] UID {item.get('uid')}: {item.get('status')}")
            print(f"[push] Sent successfully to {len(uids)} user(s)")
            return True
        else:
            print(f"[push] API error: {data}")
            return False
    except Exception as e:
        print(f"[push] Request failed: {e}")
        return False


def send_daily_report(report: str) -> bool:
    """Send the daily trending report. Splits into chunks if needed."""
    if len(report) <= MAX_CONTENT_LEN:
        return push_to_wechat(report)

    chunks = _split(report)
    ok = True
    for i, chunk in enumerate(chunks):
        title = f"<b>GitHub Trending 日报 ({i+1}/{len(chunks)})</b><br><br>"
        if not push_to_wechat(title + chunk):
            ok = False
    return ok


def _split(text: str, max_len: int = MAX_CONTENT_LEN - 500) -> list[str]:
    """Split text at paragraph boundaries."""
    chunks = []
    paragraphs = text.split("\n\n")
    current = ""

    for p in paragraphs:
        if len(current) + len(p) + 2 > max_len and current:
            chunks.append(current)
            current = p
        else:
            current = p if not current else current + "\n\n" + p

    if current:
        chunks.append(current)
    return chunks
