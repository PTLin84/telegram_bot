"""
Example reminder — template for building your own scheduled notifications.

Copy this file, rename it, and adapt the logic to your use case.
Add a cron entry to run it on your desired schedule.

Cron example (runs daily at 9:00 AM UTC):
    0 9 * * * python /path/to/telegram_bot/reminders/your_reminder.py
"""

import os
import sys
from pathlib import Path

# Make telegram_bot importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from telegram_bot.notify import send

# Load .env from telegram_bot root
_env = Path(__file__).parent.parent / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


def should_notify() -> bool:
    """Return True if the reminder should be sent, False to skip silently."""
    # Add your condition here.
    # Examples:
    #   - query a database for pending tasks
    #   - check if a file has been updated
    #   - call an API and inspect the result
    return True


def build_message() -> str:
    """Build the message string to send. Supports HTML formatting."""
    return (
        "🔔 <b>Reminder title</b>\n"
        "Your reminder details here."
    )


if __name__ == "__main__":
    if should_notify():
        msg = build_message()
        send(msg)
        print("Reminder sent.")
    else:
        print("Condition not met — skipping.")
