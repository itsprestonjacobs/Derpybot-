import discord
from discord import app_commands
from discord.ext import commands

import economy_db as db
from config import SHOP_ITEMS, BRAND_COLOR

# Look items up by name quickly.
ITEMS = {name: (price, role_name, emoji) for name, price, role_name, emoji in SHOP_ITEMS}


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="See what you can buy with your coins.")
    async def shop(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🛒 Shop", color=BRAND_COLOR,
                              description="Earn coins by chatting, then buy roles with `/buy`.")
        for name, price, role_name, emoji in SHOP_ITEMS:
            embed.add_field(name=f"{emoji} {name}", value=f"💰 {price} coins", inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(description="Buy a role from the shop.")
    @app_commands.describe(item="What to buy")
    @app_commands.choices(item=[
        app_commands.Choice(name=f"{emoji} {name} ({price})", value=name)
        for name, price, role_name, emoji in SHOP_ITEMS
    ])
    async def buy(self, interaction: discord.Interaction, item: app_commands.Choice[str]):
        price, role_name, emoji = ITEMS[item.value]

        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if not role:
            await interaction.response.send_message(
                f"The **{role_name}** role doesn't exist yet — ask an admin to create it.",
                ephemeral=True)
            return
        if role in interaction.user.roles:
            await interaction.response.send_message("You already own that!", ephemeral=True)
            return
        if db.get(interaction.user.id)["coins"] < price:
            await interaction.response.send_message(
                f"You need **{price}** coins for that. Keep chatting to earn more!", ephemeral=True)
            return

        db.add(interaction.user.id, coins=-price)
        await interaction.user.add_roles(role)
        await interaction.response.send_message(
            f"{emoji} You bought **{item.value}** for {price} coins. Enjoy your {role.mention}!")


async def setup(bot):
    await bot.add_cog(Shop(bot))
