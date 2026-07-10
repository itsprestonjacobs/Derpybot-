# Project: Ticket System

Time to put it all together. The ticket system uses almost everything you've learned:
embeds, dropdowns, **modals**, permissions, private channels, persistence, and files. When
someone opens a ticket they'll **type a reason**, and staff get a **full info panel** about
who opened it. It's the same kind of support panel the Derpy's Designs server runs.

## What we're building

A branded panel with a **dropdown**. Pick a category → a **pop-up form** asks for details →
the bot creates a **private channel** (only you + staff) showing an **info panel** about the
user → a **Close** button saves a **transcript** and deletes it. Opens and closes are
**logged**, and it all survives a restart.

## Step 0 — Server prep

Create a **Staff** role (sees tickets) and a **ticket-logs** channel (transcripts land
there).

## Step 1 — Categories live in config

Your ticket categories come from `config.py` so they're easy to change (see the setup
lesson). They're a list of `(label, description, emoji)`:

```python
# config.py
TICKET_CATEGORIES = [
    ("Place an Order", "Order a custom design or bot", "🛒"),
    ("General Support", "Questions, feedback, or help", "💬"),
    ("Payment / Refund", "Billing, invoices, and refunds", "💳"),
    ("Claim a Purchase", "Claim a purchased role or ad", "🎟️"),
    ("Partnership", "Partnerships and collaborations", "🤝"),
    ("Staff Report", "Report a problem or staff concern", "🛡️"),
]
```

**To add a ticket type, just add a row here** — no other code changes needed.

Start `cogs/tickets.py`:

```python
import io
import discord
from discord import app_commands
from discord.ext import commands

from config import (STAFF_ROLE_NAME, TICKET_CATEGORIES, TICKET_LOG_CHANNEL,
                    BANNERS, branded_embed, panel)


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(Tickets(bot))
```

## Step 2 — Creating the ticket (with a user-info panel)

The channel's first message tells staff exactly who they're helping — username, mention,
**user ID**, account age, join date, avatar — plus the reason they typed. Add this function
above the `Tickets` class:

```python
async def create_ticket(interaction, category, details):
    guild, author = interaction.guild, interaction.user

    existing = discord.utils.get(guild.text_channels, name=f"ticket-{author.id}")
    if existing:
        await interaction.response.send_message(
            f"You already have a ticket open: {existing.mention}", ephemeral=True)
        return

    staff_role = discord.utils.get(guild.roles, name=STAFF_ROLE_NAME)
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        author: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
    }
    if staff_role:
        overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

    channel = await guild.create_text_channel(
        name=f"ticket-{author.id}", overwrites=overwrites,
        topic=f"{category} ticket for {author} ({author.id})")

    joined = author.joined_at.strftime("%b %d, %Y") if author.joined_at else "Unknown"
    embed = branded_embed(title=f"🎫 {category}")
    embed.description = f"Thanks {author.mention}, a staff member will be with you soon."
    embed.set_thumbnail(url=author.display_avatar.url)
    embed.add_field(name="User", value=f"{author} ({author.mention})", inline=False)
    embed.add_field(name="User ID", value=f"`{author.id}`", inline=True)
    embed.add_field(name="Account created", value=author.created_at.strftime("%b %d, %Y"), inline=True)
    embed.add_field(name="Joined server", value=joined, inline=True)
    embed.add_field(name="Details", value=details or "*(none provided)*", inline=False)

    ping = f"{author.mention} {staff_role.mention}" if staff_role else author.mention
    await channel.send(content=ping, embed=embed, view=CloseTicket(),
                       allowed_mentions=discord.AllowedMentions(roles=True, users=True))

    log = discord.utils.get(guild.text_channels, name=TICKET_LOG_CHANNEL)
    if log:
        await log.send(f"🎫 **{author}** opened a **{category}** ticket → {channel.mention}")

    await interaction.response.send_message(f"Your ticket is ready: {channel.mention}", ephemeral=True)
```

Everything the user gives us — the `category` and the `details` they typed — goes into that
info panel. The `User ID` field is there because IDs never change, even if someone changes
their username.

## Step 3 — The reason form (a modal)

Instead of opening the ticket instantly, we pop up a **modal** so the user can explain what
they need. Add these classes above `create_ticket`:

```python
class TicketModal(discord.ui.Modal, title="Open a Ticket"):
    def __init__(self, category):
        super().__init__()
        self.category = category

    details = discord.ui.TextInput(
        label="What do you need help with?",
        placeholder="Add your reason, order details, or question here…",
        style=discord.TextStyle.paragraph, required=True, max_length=1000)

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket(interaction, self.category, self.details.value)
```

## Step 4 — The dropdown opens the form

```python
class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=l, description=d, emoji=e)
                   for l, d, e in TICKET_CATEGORIES]
        super().__init__(placeholder="Select what you need…", options=options,
                         custom_id="ticket:open")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TicketModal(self.values[0]))


class TicketPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())
```

Pick a category → the form appears → submitting it creates the ticket. That's the modal from
the UI module doing real work.

## Step 5 — Close button, transcript & logging

```python
class CloseTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red, emoji="🔒",
                       custom_id="ticket:close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        await interaction.response.send_message("Saving transcript and closing…")

        lines = []
        async for message in channel.history(limit=None, oldest_first=True):
            stamp = message.created_at.strftime("%Y-%m-%d %H:%M")
            lines.append(f"[{stamp}] {message.author}: {message.content}")
        transcript = "\n".join(lines) or "(no messages)"

        log = discord.utils.get(interaction.guild.text_channels, name=TICKET_LOG_CHANNEL)
        if log:
            file = discord.File(io.BytesIO(transcript.encode()), filename=f"{channel.name}.txt")
            await log.send(f"Transcript for `{channel.name}`", file=file)

        await channel.delete()
```

Every message is saved to a `.txt` **transcript** in `#ticket-logs` before the channel is
deleted — so you always have a full record, even after the ticket is gone.

## Step 6 — Persistence + the panel command

Add these **inside** the `Tickets` class:

```python
    async def cog_load(self):
        self.bot.add_view(TicketPanel())
        self.bot.add_view(CloseTicket())

    @app_commands.command(description="Post the ticket panel (staff only).")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ticketpanel(self, interaction: discord.Interaction):
        embeds = panel(title="🎫 | Support",
                       description="Pick an option below and tell us what you need.",
                       banner=BANNERS.get("assistance"))
        await interaction.channel.send(embeds=embeds, view=TicketPanel())
        await interaction.response.send_message("Panel posted!", ephemeral=True)
```

## Step 7 — Test the whole flow

**▶ Run the bot** and:
1. `/ticketpanel` — the branded panel appears.
2. Pick a category → **a form pops up** → type a reason → submit.
3. A private `ticket-…` channel opens with the **user-info panel** and your details, and
   `#ticket-logs` shows "ticket opened."
4. Click **Close** → a transcript lands in `#ticket-logs` and the channel deletes.
5. Restart the bot and use an old panel — still works. 🎉

## Step 8 — A Claim button for staff

So two staff don't help the same person, add a **Claim** button. Put this method **above**
the `close` method inside `CloseTicket` (buttons appear in the order they're defined):

```python
    @discord.ui.button(label="Claim", style=discord.ButtonStyle.green, emoji="🙋",
                       custom_id="ticket:claim")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("Only staff can claim tickets.", ephemeral=True)
            return
        channel = interaction.channel
        if channel.topic and "Claimed by" in channel.topic:
            await interaction.response.send_message("This ticket is already claimed.", ephemeral=True)
            return
        await channel.edit(topic=f"{channel.topic or ''} | Claimed by {interaction.user}")
        await interaction.response.send_message(f"🙋 {interaction.user.mention} claimed this ticket.")
```

It's staff-only (checks `manage_messages`), and it stamps the channel topic with the
claimer so it can't be claimed twice. **▶ Test it** — a staff member clicks Claim and it
announces who's handling the ticket.

## How to customize

- **Add/remove ticket types:** edit `TICKET_CATEGORIES` in `config.py`.
- **Ask for more info:** add another `TextInput` to `TicketModal` (up to 5).
- **Change the reason prompt:** edit the `TicketModal` field's `label`/`placeholder`.

## Recap

You built a production-style ticket system: dropdown → **reason modal** → private channel
with a **user-info panel** → **transcript** + **logging** → persistent Views. Categories live
in `config.py`, so anyone can add their own ticket types in one line.

→ **Next: Project — Economy & Leveling**
