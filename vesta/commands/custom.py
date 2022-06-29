import discord
from discord import app_commands

from vesta import partabot_client
from ..modals import CustomSlashForm, CustomMenuForm


@partabot_client.tree.command(description="Record custom commands")
@app_commands.default_permissions(ban_members=True)
@app_commands.guild_only()
@app_commands.describe(keyword="The keyword of the command")
async def custom(interaction: discord.Interaction, keyword: str):
    await interaction.response.send_modal(CustomSlashForm(keyword=keyword))


@app_commands.default_permissions(ban_members=True)
@app_commands.guild_only()
@partabot_client.tree.context_menu(name="Create Custom Command")
async def create_custom(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.send_modal(CustomMenuForm(content=message.content, author=message.author))