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
    print(f"Fetching last 50 messages from channel {CHANNEL_ID}...")
    messages = fetch_messages()
    print(f"  Retrieved {len(messages)} message(s).")

    # Track which targets have already been filled (newest message wins)
    filled = set()
    updated = []
    skipped_no_attachment = 0
    skipped_no_keyword = 0
    skipped_already_filled = 0

    for msg in messages:
        attachments = [a for a in msg.get("attachments", []) if a["filename"].endswith(".html")]
        if not attachments:
            skipped_no_attachment += 1
            continue

        content = msg.get("content", "")
        target, label = classify_message(content)
        if not target:
            skipped_no_keyword += 1
            print(f"  [NO MATCH]  .html attachment found but no keyword matched.")
            print(f"              Message text: \"{content[:120]}\"")
            print(f"              Attachment:   {attachments[0]['filename']}")
            continue

        if target in filled:
            skipped_already_filled += 1
            print(f"  [SKIP]      {label} already imported from a newer message, ignoring {attachments[0]['filename']}")
            continue

        attachment = attachments[0]
        print(f"  [IMPORTING] {label} modlist")
        print(f"              Attachment: {attachment['filename']}")
        print(f"              Saving to:  {target}")
        download_attachment(attachment["url"], target)
        filled.add(target)
        updated.append((label, attachment["filename"], target))
        print(f"  [DONE]      {label} saved successfully.")

        if len(filled) == len(KEYWORD_RULES):
            break  # found all categories, no need to look further

    print()
    print("=== Sync Summary ===")
    print(f"  Messages scanned:          {len(messages)}")
    print(f"  Skipped (no .html):        {skipped_no_attachment}")
    print(f"  Skipped (no keyword match):{skipped_no_keyword}")
    print(f"  Skipped (already filled):  {skipped_already_filled}")
    print(f"  Modlists imported:         {len(updated)}")

    if updated:
        for label, filename, target in updated:
            print(f"    - {label}: {filename} → {target}")
    else:
        print()
        print("  Nothing was imported. Possible reasons:")
        print("    - No messages had .html attachments")
        print("    - Message text didn't contain recognised keywords")
        print("    Weekly keywords:  saturday, campaign, weekly")
        print("    Joint Op keywords: joint op, jointop, operation")

if __name__ == "__main__":
    main()
