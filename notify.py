"""
Send a Telegram message to Kyle's phone.

Usage:
    python notify.py "your message here"

Or import and call from other scripts:
    from notify import send
    send("hello!")
"""

import io
import mimetypes
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


def send_file(file_path: str, caption: str = "") -> None:
    """Send a file (document) to Telegram using multipart/form-data."""
    url      = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    path     = Path(file_path)
    boundary = "----TelegramBoundary"

    def encode_field(name, value):
        return (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
            f"{value}\r\n"
        ).encode()

    def encode_file(name, filename, data):
        mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        return (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
            f"Content-Type: {mime}\r\n\r\n"
        ).encode() + data + b"\r\n"

    body = (
        encode_field("chat_id", CHAT_ID)
        + encode_field("parse_mode", "HTML")
        + (encode_field("caption", caption) if caption else b"")
        + encode_file("document", path.name, path.read_bytes())
        + f"--{boundary}--\r\n".encode()
    )

    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
    if not result.get("ok"):
        raise RuntimeError(f"Telegram error: {result}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python notify.py \"message\"")
        sys.exit(1)
    send(" ".join(sys.argv[1:]))
    print("Sent!")
