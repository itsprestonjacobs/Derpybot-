import os
import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

COGS = [
    "cogs.general",
    "cogs.embeds",
    "cogs.moderation",
    "cogs.warnings",
    "cogs.welcome",
    "cogs.roles",
    "cogs.automod",
    "cogs.logs",
    "cogs.economy",
    "cogs.shop",
    "cogs.tickets",
    "cogs.botsettings",
]


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")

    # Sync the slash commands. If we know our test server, sync to it so new
    # commands show up right away instead of waiting on Discord's global cache.
    if GUILD_ID:
        guild = discord.Object(id=int(GUILD_ID))
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
    else:
        synced = await bot.tree.sync()

    print(f"Synced {len(synced)} commands")
    print("-" * 30)


async def main():
    async with bot:
        for cog in COGS:
            await bot.load_extension(cog)
        await bot.start(TOKEN)


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("No token found. Copy .env.example to .env and paste your token.")
    asyncio.run(main())
