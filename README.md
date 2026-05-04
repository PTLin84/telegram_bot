# telegram_bot

A minimal Python package for sending Telegram messages from scripts and cron jobs.

## Setup

1. Create a bot via [@BotFather](https://t.me/BotFather) and get your token
2. Get your chat ID via `https://api.telegram.org/bot<TOKEN>/getUpdates`
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
