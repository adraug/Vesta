import typing

import discord
from discord import app_commands
import logging
import traceback

from .. import vesta_client, session_maker, lang
from ..tables import Guild, select

logger = logging.getLogger(__name__)
session = session_maker()


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class ConfigManager(app_commands.Group, name="config", description="Config Manager"):
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


config_manager = ConfigManager()


@config_manager.command(description="Set Review Channel")
@app_commands.describe(channel="The future review channel")
async def review(interaction: discord.Interaction, channel: discord.TextChannel):
    logger.debug(f"Command /config review {channel} used")

    def update(g):
        g.review_channel = channel.id
    await update_config_element(interaction, update)

    await interaction.response.send_message(lang.get("config_review", interaction.guild), ephemeral=True)


@config_manager.command(description="Set Projets Channel")
@app_commands.describe(channel="The future projects channel")
async def projects(interaction: discord.Interaction, channel: discord.TextChannel):
    logger.debug(f"Command /config projects {channel} used")

    def update(g):
        g.projects_channel = channel.id
    await update_config_element(interaction, update)

    await interaction.response.send_message(lang.get("config_projects", interaction.guild), ephemeral=True)


@config_manager.command(name="coc-role", description="Set clash of code ping role")
@app_commands.rename(coc_role="role")
@app_commands.describe(coc_role="The role to ping when a game of Clash of Code is launched")
async def change_clash_of_code_role(interaction: discord.Interaction, coc_role: discord.Role):
    logger.debug(f"Command /config coc-role {coc_role.name} used")

    def update(g):
        g.coc_role = coc_role.id
    await update_config_element(interaction, update)

    await interaction.response.send_message(lang.get("config_coc_role", interaction.guild), ephemeral=True)

@config_manager.command(name="coc-channel", description="Set clash of code channel")
@app_commands.rename(coc_channel="channel")
@app_commands.describe(coc_channel="The channel to send clash of code messages")
async def change_clash_of_code_channel(interaction: discord.Interaction, coc_channel: discord.TextChannel):
    logger.debug(f"Command /config coc-channel {coc_channel.name} used")

    def update(g):
        g.coc_channel = coc_channel.id
    await update_config_element(interaction, update)

    await interaction.response.send_message(lang.get("config_coc_channel", interaction.guild), ephemeral=True)

@config_manager.command(name="coc-cooldown", description="Set clash of code cooldown")
@app_commands.rename(coc_cooldown="cooldown")
@app_commands.describe(coc_cooldown="The cooldown between two clash of code games (in seconds)")
async def change_clash_of_code_cooldown(interaction: discord.Interaction, coc_cooldown: int):
    logger.debug(f"Command /config coc-cooldown {coc_cooldown} used")

    def update(g):
        g.coc_cooldown = coc_cooldown
    await update_config_element(interaction, update)

    await interaction.response.send_message(lang.get("config_coc_cooldown", interaction.guild), ephemeral=True)

@config_manager.command(name="lang", description="Set Guild Lang")
@app_commands.rename(guild_lang='lang')
@app_commands.describe(guild_lang="The lang for the bot")
@app_commands.choices(guild_lang=[app_commands.Choice(name=l, value=l) for l in lang.data])
async def change_lang(interaction: discord.Interaction, guild_lang: app_commands.Choice[str]):
    logger.debug(f"Command /config lang {guild_lang.value} used")

    def update(g):
        g.lang = guild_lang.value
    await update_config_element(interaction, update)

    await interaction.response.send_message(lang.get("config_lang", interaction.guild), ephemeral=True)

async def update_config_element(interaction: discord.Interaction, updater: typing.Callable[[Guild], None]):
    r = select(Guild).where(Guild.id == interaction.guild_id)
    guild = session.scalar(r)
    if not guild:
        logger.debug(f"Add guild {interaction.guild_id} to the database")
        guild = Guild(id=interaction.guild_id, name=interaction.guild.name)
        session.add(guild)

    updater(guild)

    try:
        session.commit()
    except:
        session.rollback()

        logger.error(traceback.format_exc())
        return await interaction.response.send_message(lang.get("unexpected_error", interaction.guild), ephemeral=True)
    pass

vesta_client.tree.add_command(config_manager)
