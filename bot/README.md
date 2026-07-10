# Derpy's Designs — Reference Bot

This is the **finished bot** students build toward across the course. Every code snippet in
the lessons comes from these files, so learners can always compare their work against it.

## Run it

1. Install the requirements:
   ```
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and paste your bot token (see the "Register Your Bot"
   lesson).
3. Start the bot:
   ```
   python main.py
   ```
   You should see `Logged in as ...` and `Synced N commands`.

> **Tip:** Set `GUILD_ID` in `.env` to your test server's ID so slash commands appear
> instantly instead of taking up to an hour.

## What's inside

| File | What it covers |
|------|----------------|
| `main.py` | Starts the bot, loads every cog, syncs slash commands |
| **`config.py`** | **The control panel** — studio name, colors, banners, roles, channels, ticket categories, role menu, banned words, economy rewards. Edit this to make the bot yours. |
| `data.py` | Tiny JSON load/save helper |
| `settings.py` | Per-server settings (welcome/log channels) |
| `economy_db.py` | SQLite layer for the economy system |
| `cogs/general.py` | `/ping`, `/help` |
| `cogs/embeds.py` | `/serverinfo`, `/announce`, `/embed` (custom embed builder) |
| `cogs/moderation.py` | `/kick`, `/ban`, `/unban`, `/timeout`, `/untimeout`, `/purge`, `/slowmode`, `/lock`, `/unlock`, `/nick`, `/role` — all logged to `#mod-logs` |
| `cogs/warnings.py` | `/warn`, `/warnings`, `/clearwarns` (saved to JSON) |
| `cogs/welcome.py` | Welcome & leave messages + auto "Member" role |
| `cogs/roles.py` | `/rolemenu` — button self-roles |
| `cogs/automod.py` | Word filter, invite blocking, anti-spam |
| `cogs/logs.py` | Mod-log for deletes, edits, joins, leaves |
| `cogs/economy.py` | `/balance`, `/daily`, `/pay`, `/leaderboard`, XP & levels |
| `cogs/shop.py` | `/shop`, `/buy` — spend coins on roles (items in `config.py`) |
| `cogs/tickets.py` | `/ticketpanel` — dropdown → reason **modal** → private channel with a **user-info panel** → **Claim** + **Close** (transcript + logging) |
| `cogs/botsettings.py` | `/set_welcome`, `/set_logs` |

> **Customizing:** almost everything (names, colors, roles, channels, ticket categories,
> role menu, banned words, rewards) lives in `config.py`. Edit it there — the cogs read from
> it, so you rarely touch them.

## Server setup

- Create a role named **Staff** (or set `STAFF_ROLE_NAME` in `.env`) — it can see tickets.
- Optional channels: **welcome**, **mod-logs**, **ticket-logs** (or set them with
  `/set_welcome` and `/set_logs`).
- Create roles named **Announcements**, **Events**, **Updates** for the role menu, and
  optionally a **Member** role for auto-assign.
- Drag the bot's role **above** the members/roles it manages, or Discord will refuse the
  action.

## Test checklist

Do this in a **test server you own**.

- [ ] Bot comes online and prints `Synced N commands`.
- [ ] `/ping` and `/help` work.
- [ ] `/serverinfo` and `/announce` post embeds.
- [ ] `/kick`, `/timeout minutes:1`, `/purge amount:5` work; refused without permission.
- [ ] `/warn`, `/warnings`, `/clearwarns` — warnings persist across a restart.
- [ ] `/rolemenu` posts buttons that toggle roles.
- [ ] Auto-mod deletes a test banned word and invite links.
- [ ] Chatting earns XP/coins; `/balance`, `/daily`, `/pay`, `/leaderboard` work.
- [ ] `/ticketpanel` → pick a category → private channel → **Close** saves a transcript.
- [ ] Restart the bot; ticket panel and role menu still work (persistent views).

> The bot generates `economy.db`, `warnings.json`, and `settings.json` at runtime. These are
> git-ignored — don't commit them.
