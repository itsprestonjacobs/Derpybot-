import io

import discord
from discord import app_commands
from discord.ext import commands

from config import (STAFF_ROLE_NAME, TICKET_CATEGORIES, TICKET_LOG_CHANNEL,
                    BANNERS, branded_embed, panel)


async def create_ticket(interaction: discord.Interaction, category: str, details: str):
    guild, author = interaction.guild, interaction.user

    # One open ticket per person.
    existing = discord.utils.get(guild.text_channels, name=f"ticket-{author.id}")
    if existing:
        await interaction.response.send_message(
            f"You already have a ticket open: {existing.mention}", ephemeral=True)
        return

    staff_role = discord.utils.get(guild.roles, name=STAFF_ROLE_NAME)

    # Hide from everyone; allow the author, staff, and the bot.
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

    # An info panel so staff instantly know who opened this and why.
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

    # Log that a ticket was opened.
    log_channel = discord.utils.get(guild.text_channels, name=TICKET_LOG_CHANNEL)
    if log_channel:
        await log_channel.send(f"🎫 **{author}** opened a **{category}** ticket → {channel.mention}")

    await interaction.response.send_message(f"Your ticket is ready: {channel.mention}", ephemeral=True)


class TicketModal(discord.ui.Modal, title="Open a Ticket"):
    """Pops up when a category is chosen, so the user can add a reason/details."""

    def __init__(self, category):
        super().__init__()
        self.category = category

    details = discord.ui.TextInput(
        label="What do you need help with?",
        placeholder="Add your reason, order details, or question here…",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket(interaction, self.category, self.details.value)


class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=l, description=d, emoji=e)
                   for l, d, e in TICKET_CATEGORIES]
        super().__init__(placeholder="Select what you need…", options=options,
                         custom_id="ticket:open")

    async def callback(self, interaction: discord.Interaction):
        # Open the modal so they can add a reason before the ticket is made.
        await interaction.response.send_modal(TicketModal(self.values[0]))


class TicketPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())


class CloseTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

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

        log_channel = discord.utils.get(interaction.guild.text_channels, name=TICKET_LOG_CHANNEL)
        if log_channel:
            file = discord.File(io.BytesIO(transcript.encode()), filename=f"{channel.name}.txt")
            await log_channel.send(f"Transcript for `{channel.name}`", file=file)

        await channel.delete()


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.add_view(TicketPanel())
        self.bot.add_view(CloseTicket())

    @app_commands.command(description="Post the ticket panel in this channel (staff only).")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ticketpanel(self, interaction: discord.Interaction):
        embeds = panel(title="🎫 | Support",
                       description="Need a hand? Pick an option from the dropdown below and "
                                   "tell us what you need — we'll open a private ticket for you.",
                       banner=BANNERS.get("assistance"))
        await interaction.channel.send(embeds=embeds, view=TicketPanel())
        await interaction.response.send_message("Panel posted!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Tickets(bot))
