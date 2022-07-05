import discord
from discord import app_commands
import logging
import traceback
import re

from .. import vesta_client, session, lang
from ..modals import CustomSlashForm, CustomMenuForm
from ..tables import CustomCommand, select

logger = logging.getLogger(__name__)

custom_regex = "^[a-z0-9_-]{1,32}$"

@app_commands.guild_only()
@app_commands.default_permissions(ban_members=True)
class CustomManager(app_commands.Group, name="custom", description="Custom commands manager"):
    async def on_error(self, interaction: discord.Interaction, error):
        logger.debug(f"Error {error} raised")
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                lang.get("permissions_error", interaction.guild), ephemeral=True)
        elif isinstance(error, app_commands.errors.BotMissingPermissions):
            await interaction.response.send_message(
                lang.get("bot_permissions_error", interaction.guild) + f" {', '.join(error.missing_permissions)}",
                ephemeral=True)
        else:
            logger.error(traceback.format_exc())
            await interaction.response.send_message(lang.get("unexpected_error", interaction.guild), ephemeral=True)


custom_manager = CustomManager()


@custom_manager.command(description="Create custom command")
@app_commands.describe(keyword="The keyword of the command")
async def add(interaction: discord.Interaction, keyword: str):
    keyword = keyword.lower()
    if not re.match(custom_regex, keyword):
        return await interaction.response.send_message(lang.get("invalid_keyword", interaction.guild), ephemeral=True)
    logger.debug(f"Command /custom add {keyword} used")

    if len(keyword) > 32:
        return await interaction.response.send_message(lang.get("too_long_keyword", interaction.guild), ephemeral=True)

    r = select(CustomCommand).where(CustomCommand.guild_id == interaction.guild_id)
    r = r.where(CustomCommand.keyword == keyword)

    command = session.scalar(r)
    if command:
        return await interaction.response.send_message(lang.get("command_already_exist", interaction.guild), ephemeral=True)

    number = session.query(CustomCommand).where(CustomCommand.guild_id == interaction.guild_id).count()
    if number > 39:
        return await interaction.response.send_message(lang.get("too_much_commands", interaction.guild), ephemeral=True)

    await interaction.response.send_modal(CustomSlashForm(keyword=keyword, interaction=interaction))


@custom_manager.command(description="Remove custom command")
@app_commands.describe(keyword="The keyword of the command")
async def remove(interaction: discord.Interaction, keyword: str):
    keyword = keyword.lower()

    logger.debug(f"Command /custom remove {keyword} used")
    r = select(CustomCommand).where(CustomCommand.guild_id == interaction.guild_id)
    r = r.where(CustomCommand.keyword == keyword)

    command = session.scalar(r)
    if not command:
        return await interaction.response.send_message(lang.get("command_not_exist", interaction.guild), ephemeral=True)
    vesta_client.tree.remove_command(keyword, guild=interaction.guild)
    await vesta_client.tree.sync()
    session.delete(command)
    session.commit()
    await interaction.response.send_message(lang.get("command_deleted", interaction.guild), ephemeral=True)
    await vesta_client.tree.sync(guild=interaction.guild)


@custom_manager.command(name="list", description="List custom commands")
async def custom_list(interaction: discord.Interaction):
    logger.debug(f"Command /custom list used")
    list_embed = discord.Embed(title=lang.get("list_commands", interaction.guild))
    list_embed2 = discord.Embed(title=lang.get("list_commands2", interaction.guild))

    r = select(CustomCommand).where(CustomCommand.guild_id == interaction.guild_id)
    commands = session.scalars(r)

    multiple = False

    for index, command in enumerate(commands):
        if index < 25:
            list_embed.add_field(name=command.keyword, value=command.title, inline=False)
        else:
            multiple = True
            list_embed2.add_field(name=command.keyword, value=command.title, inline=False)

    embeds = [list_embed]
    if multiple:
        embeds.append(list_embed2)
    await interaction.response.send_message(embeds=embeds, ephemeral=True)


@app_commands.default_permissions(ban_members=True)
@app_commands.guild_only()
@vesta_client.tree.context_menu(name="Create Custom Command")
async def create_custom(interaction: discord.Interaction, message: discord.Message):
    logger.debug(f"Menu Create Custom Command used")

    number = session.query(CustomCommand).where(CustomCommand.guild_id == interaction.guild_id).count()
    if number > 39:
        return await interaction.response.send_message(lang.get("too_much_commands", interaction.guild), ephemeral=True)

    await interaction.response.send_modal(CustomMenuForm(content=message.content, author=message.author, interaction=interaction))

vesta_client.tree.add_command(custom_manager)
