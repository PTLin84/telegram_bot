"""
Send a Telegram message to Kyle's phone.

Usage:
    python notify.py "your message here"

Or import and call from other scripts:
    from notify import send
    send("hello!")
"""

import os
import sys
import urllib.request
import urllib.parse
import json
from pathlib import Path

# Load .env
_env = Path(__file__).parent / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

TOKEN   = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def send(message: str) -> None:
    url  = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id":    CHAT_ID,
        "text":       message,
        "parse_mode": "HTML",
    }).encode()
    req  = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read())
    if not result.get("ok"):
        raise RuntimeError(f"Telegram error: {result}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python notify.py \"message\"")
        sys.exit(1)
    send(" ".join(sys.argv[1:]))
    print("Sent!")
