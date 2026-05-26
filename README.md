# telegram_bot

A minimal Python package for sending Telegram messages from scripts and cron jobs.

## Setup

1. Create a bot via [@BotFather](https://t.me/BotFather) and get your token
2. Get your chat ID via `https://api.telegram.org/bot<TOKEN>/getUpdates` or via [@Get_miidrobot](https://t.me/Get_miidrobot)
3. Copy `.env.example` to `.env` and fill in your credentials:

```
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

## Usage

**From the command line:**
```bash
python notify.py "Hello from your PC!"
```

**From another script:**
```python
import sys
sys.path.insert(0, "/path/to/telegram_bot")
from notify import send

send("Hello!")
```

**As a package:**
```python
from telegram_bot import send

send("Hello!")
```

---

## Group Summary Bot

A Telegram bot that records all messages in a group and summarizes them on demand using Claude AI. Summary is posted back to the group, visible to all members.

### How it works

1. Add `@kyle_claude_agent_bot` to your Telegram group as a regular member
2. **Disable privacy mode** via BotFather → `/mybots` → Bot Settings → Group Privacy → Turn off (required to receive all messages, not just commands)
3. Run the bot on your PC — it uses long polling (no public URL or webhook needed)
4. Every message is saved to a local SQLite DB (`group_reader/messages.db`)
5. Anyone in the group can call `/summarize` — the bot sends the transcript to Claude and posts the structured summary back to the group

### Setup

```bash
# Add ANTHROPIC_API_KEY to .env
echo "ANTHROPIC_API_KEY=your_key_here" >> .env

# Run the bot
cd group_reader
python bot.py
```

### Commands

| Command | Description |
|---|---|
| `/summarize` | Summarize the last 100 messages |
| `/summarize 50` | Summarize the last N messages (max 500) |
| `/chatid` | Show the current group's chat ID |
| `/groups` | List all groups the bot has seen (sends to your DM) |
| `/help` | Show available commands in Traditional Chinese |

### File layout

```
group_reader/
├── bot.py          # Long polling loop + command handler
├── store.py        # SQLite message store
├── summarizer.py   # Claude API call (Sonnet, auto-detects language)
└── messages.db     # Local message database (gitignored)
```

### Notes

- The bot only records messages sent **after** it joins the group
- The bot must be running on your PC to receive messages; queued messages (up to 24h) are delivered when it restarts
- Summaries are structured: Key Topics, Decisions/Conclusions, Open Questions, Tone
