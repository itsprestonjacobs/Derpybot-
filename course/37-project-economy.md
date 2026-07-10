# Project: Economy & Leveling

Our second capstone: a coins-and-levels system, the kind that keeps communities active.
Members earn coins by chatting, level up, check a leaderboard, and spend coins. It's the
perfect project to cement **databases**, **events**, and **embeds** together.

## What we're building

- Earn **coins** and **XP** for chatting.
- **Level up** automatically (with an announcement).
- `/balance`, `/daily`, `/pay`, and `/leaderboard` commands.

## Step 1 — The database layer

Using what you learned in the SQLite lesson, make `economy_db.py`:

```python
import sqlite3

conn = sqlite3.connect("economy.db")
conn.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    coins INTEGER DEFAULT 0,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 0,
    last_daily TEXT
)""")
conn.commit()


def _ensure(user_id):
    conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))

def get(user_id):
    _ensure(user_id)
    row = conn.execute("SELECT coins, xp, level, last_daily FROM users WHERE user_id=?",
                       (user_id,)).fetchone()
    return {"coins": row[0], "xp": row[1], "level": row[2], "last_daily": row[3]}

def add(user_id, coins=0, xp=0):
    _ensure(user_id)
    conn.execute("UPDATE users SET coins=coins+?, xp=xp+? WHERE user_id=?",
                 (coins, xp, user_id))
    conn.commit()

def set_level(user_id, level):
    conn.execute("UPDATE users SET level=? WHERE user_id=?", (level, user_id))
    conn.commit()

def set_daily(user_id, when):
    conn.execute("UPDATE users SET last_daily=? WHERE user_id=?", (when, user_id))
    conn.commit()

def top(limit=10):
    return conn.execute("SELECT user_id, coins, level FROM users ORDER BY coins DESC LIMIT ?",
                        (limit,)).fetchall()
```

## Step 2 — Earn XP by chatting

Make `cogs/economy.py`. First, the listener that rewards messages:

```python
import datetime
import discord
from discord import app_commands
from discord.ext import commands

import economy_db as db


def xp_for_level(level):
    return 5 * (level ** 2) + 50 * level + 100      # XP needed for the next level


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        db.add(message.author.id, coins=1, xp=5)     # reward each message

        stats = db.get(message.author.id)
        needed = xp_for_level(stats["level"])
        if stats["xp"] >= needed:
            new_level = stats["level"] + 1
            db.set_level(message.author.id, new_level)
            await message.channel.send(
                f"🎉 {message.author.mention} reached **level {new_level}**!")


async def setup(bot):
    await bot.add_cog(Economy(bot))
```

Add `"cogs.economy"` to `COGS`. **▶ Chat a few times** and watch yourself level up. (Needs
the Message Content Intent.)

## Step 3 — /balance

```python
    @app_commands.command(description="Check your balance and level.")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        s = db.get(member.id)
        embed = discord.Embed(title=f"{member.display_name}'s stats",
                              color=discord.Color.gold())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="💰 Coins", value=s["coins"])
        embed.add_field(name="⭐ Level", value=s["level"])
        embed.add_field(name="✨ XP", value=f"{s['xp']} / {xp_for_level(s['level'])}")
        await interaction.response.send_message(embed=embed)
```

`member = member or interaction.user` makes the argument optional — check your own or
someone else's.

## Step 4 — /daily reward

```python
    @app_commands.command(description="Claim your daily coins.")
    async def daily(self, interaction: discord.Interaction):
        today = datetime.date.today().isoformat()
        s = db.get(interaction.user.id)
        if s["last_daily"] == today:
            await interaction.response.send_message(
                "You already claimed your daily today. Come back tomorrow!", ephemeral=True)
            return
        db.add(interaction.user.id, coins=100)
        db.set_daily(interaction.user.id, today)
        await interaction.response.send_message("💰 You claimed **100** daily coins!")
```

We store the date of the last claim and compare it to today — a neat use of persistent data.

## Step 5 — /pay

```python
    @app_commands.command(description="Give coins to another member.")
    @app_commands.describe(member="Who to pay", amount="How much")
    async def pay(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if amount <= 0:
            await interaction.response.send_message("Amount must be positive.", ephemeral=True)
            return
        if db.get(interaction.user.id)["coins"] < amount:
            await interaction.response.send_message("You don't have enough coins.", ephemeral=True)
            return
        db.add(interaction.user.id, coins=-amount)
        db.add(member.id, coins=amount)
        await interaction.response.send_message(
            f"💸 {interaction.user.mention} paid {member.mention} **{amount}** coins!")
```

## Step 6 — /leaderboard

This is where the database pays off — one query, sorted:

```python
    @app_commands.command(description="Show the richest members.")
    async def leaderboard(self, interaction: discord.Interaction):
        rows = db.top(10)
        lines = []
        for i, (user_id, coins, level) in enumerate(rows, start=1):
            member = interaction.guild.get_member(user_id)
            name = member.display_name if member else f"User {user_id}"
            lines.append(f"**{i}.** {name} — 💰 {coins} (lvl {level})")
        embed = discord.Embed(title="🏆 Leaderboard", description="\n".join(lines) or "No data yet.",
                              color=discord.Color.gold())
        await interaction.response.send_message(embed=embed)
```

## Step 7 — A shop (spend coins on roles)

Earning coins is only fun if you can spend them. Let's add a shop that sells roles. Keep the
items in `config.py` so they're easy to change — `(name, price, role name, emoji)`:

```python
# config.py
SHOP_ITEMS = [
    ("VIP", 1000, "VIP", "⭐"),
    ("Supporter", 500, "Supporter", "💖"),
    ("Custom Color", 750, "Custom Color", "🎨"),
]
```

Make `cogs/shop.py`:

```python
import discord
from discord import app_commands
from discord.ext import commands

import economy_db as db
from config import SHOP_ITEMS, BRAND_COLOR

ITEMS = {name: (price, role, emoji) for name, price, role, emoji in SHOP_ITEMS}


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="See what you can buy.")
    async def shop(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🛒 Shop", color=BRAND_COLOR,
                              description="Earn coins by chatting, then buy roles with `/buy`.")
        for name, price, role, emoji in SHOP_ITEMS:
            embed.add_field(name=f"{emoji} {name}", value=f"💰 {price} coins", inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(description="Buy a role.")
    @app_commands.choices(item=[
        app_commands.Choice(name=f"{emoji} {name} ({price})", value=name)
        for name, price, role, emoji in SHOP_ITEMS
    ])
    async def buy(self, interaction: discord.Interaction, item: app_commands.Choice[str]):
        price, role_name, emoji = ITEMS[item.value]
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if not role:
            await interaction.response.send_message("That role doesn't exist yet.", ephemeral=True)
            return
        if role in interaction.user.roles:
            await interaction.response.send_message("You already own that!", ephemeral=True)
            return
        if db.get(interaction.user.id)["coins"] < price:
            await interaction.response.send_message("Not enough coins — keep chatting!", ephemeral=True)
            return
        db.add(interaction.user.id, coins=-price)
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"{emoji} You bought **{item.value}**! Enjoy your {role.mention}.")


async def setup(bot):
    await bot.add_cog(Shop(bot))
```

Add `"cogs.shop"` to `COGS`, create the roles (**VIP**, **Supporter**, **Custom Color**)
below the bot's role, and **▶ try** `/shop` then `/buy`. Notice `@app_commands.choices`
builds the dropdown of items straight from `SHOP_ITEMS` — add an item to the config and it
appears automatically.

## Take it further

- A `rank` card image, or XP roles that auto-assign at certain levels.
- A `/gamble` command, or interest on savings.
- Make purchased roles temporary with the tasks/scheduling you learned.

## Recap

- Store coins/xp/level in **SQLite** via a clean `economy_db.py`.
- Reward chatting in `on_message`; level up when XP crosses a threshold.
- Commands: `/balance`, `/daily` (date-gated), `/pay`, `/leaderboard` (one sorted query).
- You just combined databases, events, and embeds into a real feature. 🎉

→ **Next: Background Tasks & Scheduling**
