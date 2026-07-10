import os

import discord

# ============================================================
#  ⚙️  BOT CONFIG — this is your control panel.
#  Change things HERE to make the bot yours. You should almost
#  never need to edit the files in the cogs/ folder.
# ============================================================

# ---- Branding -------------------------------------------------
STUDIO_NAME = "Derpy's Designs"
TAGLINE = "Where Creativity Meets Precision"
BRAND_COLOR = discord.Color.from_str("#1e9bff")   # main embed color (any hex)

# Banner images shown on top of panels. Upload an image to any Discord
# channel, right-click it -> Copy Link, and paste it here. None = no banner.
BANNERS = {
    "welcome": None,
    "assistance": None,
    "market": None,
}
DIVIDER_IMAGE = None      # the thin bar shown at the bottom of a panel

# ---- Roles (match the names in YOUR server exactly) -----------
STAFF_ROLE_NAME = os.getenv("STAFF_ROLE_NAME", "Staff")   # can see/manage tickets
AUTO_ROLE_NAME = "Member"        # auto-given to new members (set to None to disable)

# ---- Channels (by name — create these in your server) ---------
WELCOME_CHANNEL = "welcome"          # welcome & goodbye messages
LOG_CHANNEL = "mod-logs"             # moderation / server logs
TICKET_LOG_CHANNEL = "ticket-logs"   # closed-ticket transcripts

# ---- Self-role menu:  (button label, emoji, role name) --------
ROLE_BUTTONS = [
    ("Announcements", "📢", "Announcements"),
    ("Events", "🎉", "Events"),
    ("Updates", "🔔", "Updates"),
]

# ---- Ticket categories:  (label, description, emoji) ----------
# Add, remove, or rename rows to change what people can open a ticket for.
TICKET_CATEGORIES = [
    ("Place an Order", "Order a custom design or bot", "🛒"),
    ("General Support", "Questions, feedback, or help", "💬"),
    ("Payment / Refund", "Billing, invoices, and refunds", "💳"),
    ("Claim a Purchase", "Claim a purchased role or ad", "🎟️"),
    ("Partnership", "Partnerships and collaborations", "🤝"),
    ("Staff Report", "Report a problem or staff concern", "🛡️"),
]

# ---- Auto-moderation ------------------------------------------
BANNED_WORDS = ["scam", "free nitro"]     # lowercase
BLOCK_INVITE_LINKS = True

# ---- Economy --------------------------------------------------
COINS_PER_MESSAGE = 1
XP_PER_MESSAGE = 5
DAILY_REWARD = 100

# ---- Shop:  (item name, price, role name to grant, emoji) -----
# The role must exist in your server and sit BELOW the bot's role.
SHOP_ITEMS = [
    ("VIP", 1000, "VIP", "⭐"),
    ("Supporter", 500, "Supporter", "💖"),
    ("Custom Color", 750, "Custom Color", "🎨"),
]


# ============================================================
#  Helpers used across the bot. You can leave these alone.
# ============================================================

def branded_embed(title=None, description=None):
    """A normal embed already wearing our color and footer."""
    embed = discord.Embed(title=title, description=description, color=BRAND_COLOR)
    embed.set_footer(text=f"{STUDIO_NAME} • {TAGLINE}")
    return embed


def panel(title, description, banner=None):
    """The 'panel' look: an optional banner on top, the titled content,
    then the divider bar. Returns a LIST of embeds — send with embeds=panel(...)."""
    embeds = []
    if banner:
        top = discord.Embed(color=BRAND_COLOR)
        top.set_image(url=banner)
        embeds.append(top)

    body = discord.Embed(title=title, description=description, color=BRAND_COLOR)
    if DIVIDER_IMAGE:
        body.set_image(url=DIVIDER_IMAGE)
    body.set_footer(text=f"{STUDIO_NAME} • {TAGLINE}")
    embeds.append(body)
    return embeds
