"""
Summarize a list of group messages using Claude Sonnet.
"""

import anthropic


def summarize(messages: list[dict], language: str = "auto") -> str:
    if not messages:
        return "No messages to summarize."

    # Format messages as transcript
    lines = []
    for m in messages:
        text = m.get("text", "").strip()
        if not text or text.startswith("/"):
            continue
        sender = m.get("sender") or "Unknown"
        ts     = m.get("timestamp", "")[:10]
        lines.append(f"[{ts}] {sender}: {text}")
    transcript = "\n".join(lines)

    lang_instruction = {
        "en":   "Respond in English.",
        "zh":   "請用繁體中文回覆。",
        "auto": "Detect the dominant language of the messages and respond in that language.",
    }.get(language, "Respond in English.")

    prompt = f"""You are summarizing a Telegram group chat conversation.

{lang_instruction}

Here are the messages ({len(messages)} total):

{transcript}

Provide a structured summary with these sections:
1. Key Topics — main subjects discussed
2. Decisions / Conclusions — anything agreed upon or resolved
3. Open Questions / Action Items — unresolved items or tasks

Formatting rules (Telegram HTML):
- Use <b>section title</b> for each section header
- Use • for bullet points (plain text, no dashes or asterisks)
- Use <i>text</i> only for emphasis if needed
- Do NOT use markdown (no ##, no **, no __)
- Keep line breaks between sections

Be concise. Mention group members by name when relevant. Skip sections that are not applicable."""

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()
