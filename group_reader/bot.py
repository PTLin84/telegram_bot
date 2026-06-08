"""
Telegram group reader bot — polls for new messages, stores them,
and summarizes on /summarize command.

Usage:
    python bot.py

Commands (send in the group or as DM):
    /summarize       — summarize last 100 messages from this group
    /summarize 50    — summarize last 50 messages
    /chatid          — report the current chat's ID (useful for setup)
    /groups          — list all groups the bot has seen (DM only)
"""

import json
import os
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

# Load .env
_env = Path(__file__).parent.parent / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

import store
import summarizer

TOKEN   = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]  # Kyle's personal DM chat ID
BASE    = f"https://api.telegram.org/bot{TOKEN}"

store.init_db()


def api_call(method: str, params: dict = None) -> dict:
    url  = f"{BASE}/{method}"
    data = urllib.parse.urlencode(params or {}).encode()
    req  = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=35) as resp:
        return json.loads(resp.read())


def send_message(chat_id: int | str, text: str):
    api_call("sendMessage", {
        "chat_id":    chat_id,
        "text":       text,
        "parse_mode": "HTML",
    })


def handle_update(update: dict):
    msg = update.get("message") or update.get("channel_post")
    if not msg:
        return

    chat      = msg.get("chat", {})
    group_id  = chat.get("id")
    group_name = chat.get("title") or chat.get("username") or str(group_id)
    message_id = msg.get("message_id")
    text       = msg.get("text") or msg.get("caption", "")
    ts         = datetime.fromtimestamp(msg["date"], tz=timezone.utc).isoformat()

    # Sender name
    sender = None
    if "from" in msg:
        f = msg["from"]
        sender = f.get("first_name", "")
        if f.get("last_name"):
            sender += " " + f["last_name"]
        sender = sender.strip() or f.get("username") or "Unknown"

    # Always save the message (even commands)
    if text:
        store.save_message(group_id, group_name, message_id, sender, text, ts)

    # Handle commands
    if text.startswith("/help"):
        send_message(group_id,
            "🤖 <b>群組摘要機器人</b>\n\n"
            "<b>運作方式：</b>\n"
            "我會記錄群組內的所有訊息。"
            "當你呼叫摘要指令時，我會將近期訊息送給 Claude AI 分析，"
            "並將結果發布在群組內供所有成員查看。\n\n"
            "<b>指令：</b>\n"
            "<code>/summarize</code> — 摘要最近 100 則訊息\n"
            "<code>/summarize 50</code> — 摘要最近 N 則訊息（最多 500）\n"
            "<code>/chatid</code> — 顯示此群組的 Chat ID\n"
            "<code>/help</code> — 顯示此說明\n\n"
            "<i>注意：機器人只會記錄加入群組後的訊息。</i>"
        )

    elif text.startswith("/chatid"):
        send_message(group_id, f"Chat ID: `{group_id}`\nName: {group_name}")

    elif text.startswith("/groups"):
        groups = store.list_groups()
        if groups:
            lines = [f"• {g['group_name']} (`{g['group_id']}`) — {g['msg_count']} messages"
                     for g in groups]
            send_message(CHAT_ID, "Groups seen:\n" + "\n".join(lines))
        else:
            send_message(CHAT_ID, "No groups yet.")

    elif text.startswith("/summarize"):
        parts = text.strip().split()
        limit = 100
        if len(parts) > 1 and parts[1].isdigit():
            limit = min(int(parts[1]), 500)

        messages = store.get_recent(group_id, limit)
        if not messages:
            send_message(group_id, "尚無儲存的訊息。")
            return

        send_message(group_id, f"⏳ 正在摘要最近 {len(messages)} 則訊息…")
        try:
            summary = summarizer.summarize(messages)
            header  = f"📋 最近 {len(messages)} 則訊息\n\n"
            send_message(group_id, header + summary)
        except Exception as e:
            send_message(group_id, f"❌ 摘要失敗：{e}")


def run():
    print("Bot started. Polling for updates…")
    offset = None
    while True:
        try:
            params = {"timeout": 30, "allowed_updates": ["message", "channel_post"]}
            if offset:
                params["offset"] = offset
            result = api_call("getUpdates", params)
            for update in result.get("result", []):
                handle_update(update)
                offset = update["update_id"] + 1
        except KeyboardInterrupt:
            print("\nStopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    run()
