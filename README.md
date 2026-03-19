# Task Force Phalanx – Mod Selector

A web-based Arma 3 mod selector for Task Force Phalanx. Members can browse the current modlists, select which mods they want, and download a ready-to-import Arma 3 Launcher preset file.

**Live site:** https://loltorres9.github.io/TFP-Mods/

---

## Features

- Browse Weekly Mission, Joint Op, Core, and Optional mods
- Select/deselect individual mods or entire categories
- Download a custom `.html` preset file importable directly into the Arma 3 Launcher
- Modlists auto-sync from Discord every 5 minutes — no manual uploads needed

---

## How the Auto-Sync Works

Modlists are posted as `.html` attachments in the Discord modlist channel. A GitHub Actions workflow runs every 5 minutes, checks the channel for new files, and automatically commits them to the repo.

**Keyword detection** — the script reads the message text to determine which modlist slot to update:

| Keywords in message | Updates file |
|---|---|
| `saturday`, `campaign`, `weekly` | `mission_mods.html` (Weekly Mission Mods) |
| `joint op`, `operation` | `taskforce_phalanx_mods_JointOp.html` (Joint Op Mods) |

Core and Optional mods (`taskforce_phalanx_mods core.html`, `taskforce_phalanx_mods_optional.html`) are managed manually.

---

## Setup

### Requirements
- A Discord bot with **Read Message History** and **View Channels** permissions in the modlist channel
- Two GitHub repository secrets:
  - `DISCORD_BOT_TOKEN` — your Discord bot token
  - `DISCORD_CHANNEL_ID` — the ID of the modlist channel

### Manually triggering a sync
Go to **Actions** → **Sync Modlists from Discord** → **Run workflow**.

---

## Repository Structure

```
TFP-Mods/
├── index.html                          # Main mod selector website
├── mission_mods.html                   # Weekly mission modlist (auto-updated)
├── taskforce_phalanx_mods_JointOp.html # Joint Op modlist (auto-updated)
├── taskforce_phalanx_mods core.html    # Core mods (manual)
├── taskforce_phalanx_mods_optional.html# Optional mods (manual)
└── scripts/
    └── sync_discord.py                 # Discord sync script
```
