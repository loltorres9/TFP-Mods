#!/usr/bin/env python3
"""
Fetches the latest .html modlist attachments from a Discord channel
and saves them to fixed repo filenames based on message keywords.
"""

import os
import sys
import requests

DISCORD_API = "https://discord.com/api/v10"
BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
CHANNEL_ID = os.environ["DISCORD_CHANNEL_ID"]

HEADERS = {"Authorization": f"Bot {BOT_TOKEN}"}

# Keyword rules: if the message text contains any of these words (case-insensitive),
# the attachment maps to the given repo filename.
KEYWORD_RULES = [
    {
        "keywords": ["joint op", "jointop", "operation", "joint operation"],
        "target": "taskforce_phalanx_mods_JointOp.html",
        "label": "Joint Op",
    },
    {
        "keywords": ["saturday", "campaign", "weekly", "saturday campaign"],
        "target": "mission_mods.html",
        "label": "Weekly Mission",
    },
]

def fetch_messages(limit=50):
    resp = requests.get(
        f"{DISCORD_API}/channels/{CHANNEL_ID}/messages",
        headers=HEADERS,
        params={"limit": limit},
    )
    resp.raise_for_status()
    return resp.json()

def classify_message(content):
    """Return the target filename for a message, or None if unrecognised."""
    lower = content.lower()
    for rule in KEYWORD_RULES:
        if any(kw in lower for kw in rule["keywords"]):
            return rule["target"], rule["label"]
    return None, None

def download_attachment(url, filename):
    resp = requests.get(url)
    resp.raise_for_status()
    with open(filename, "wb") as f:
        f.write(resp.content)

def main():
    print(f"Fetching messages from channel {CHANNEL_ID}...")
    messages = fetch_messages()

    # Track which targets have already been filled (newest message wins)
    filled = set()
    updated = []

    for msg in messages:
        attachments = [a for a in msg.get("attachments", []) if a["filename"].endswith(".html")]
        if not attachments:
            continue

        target, label = classify_message(msg.get("content", ""))
        if not target:
            print(f"  Skipped (no keyword match): message {msg['id'][:8]}… — \"{msg.get('content','')[:80]}\"")
            continue

        if target in filled:
            continue  # already have the latest for this category

        attachment = attachments[0]
        print(f"  {label}: {attachment['filename']} → {target}")
        download_attachment(attachment["url"], target)
        filled.add(target)
        updated.append(target)

        if len(filled) == len(KEYWORD_RULES):
            break  # found all categories, no need to look further

    if not updated:
        print("No modlist attachments matched. Check that message text contains recognised keywords.")
        print("  Weekly keywords: saturday, campaign, weekly")
        print("  Joint Op keywords: joint op, operation")
    else:
        print(f"\nUpdated {len(updated)} file(s): {', '.join(updated)}")

if __name__ == "__main__":
    main()
