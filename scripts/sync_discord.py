#!/usr/bin/env python3
"""
Fetches the latest .html modlist attachments from a Discord channel
and saves them to the repo root, overwriting existing files.
"""

import os
import sys
import requests

DISCORD_API = "https://discord.com/api/v10"
BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
CHANNEL_ID = os.environ["DISCORD_CHANNEL_ID"]

HEADERS = {"Authorization": f"Bot {BOT_TOKEN}"}

# Known modlist filenames — attachments matching these will be saved
KNOWN_FILES = {
    "mission_mods.html",
    "taskforce_phalanx_mods core.html",
    "taskforce_phalanx_mods_JointOp.html",
    "taskforce_phalanx_mods_optional.html",
}

def fetch_messages(limit=50):
    resp = requests.get(
        f"{DISCORD_API}/channels/{CHANNEL_ID}/messages",
        headers=HEADERS,
        params={"limit": limit},
    )
    resp.raise_for_status()
    return resp.json()

def download_attachment(url, filename):
    resp = requests.get(url)
    resp.raise_for_status()
    # Save to repo root (script is run from the repo root)
    with open(filename, "wb") as f:
        f.write(resp.content)
    print(f"  Saved: {filename}")

def main():
    print(f"Fetching messages from channel {CHANNEL_ID}...")
    messages = fetch_messages()

    # Track the most recent attachment per filename (first match wins since
    # messages are returned newest-first)
    seen = set()
    updated = []

    for msg in messages:
        for attachment in msg.get("attachments", []):
            name = attachment["filename"]
            if name in KNOWN_FILES and name not in seen:
                seen.add(name)
                print(f"Found: {name} (message {msg['id']})")
                download_attachment(attachment["url"], name)
                updated.append(name)

    if not updated:
        print("No modlist attachments found.")
    else:
        print(f"\nUpdated {len(updated)} file(s): {', '.join(updated)}")

if __name__ == "__main__":
    main()
