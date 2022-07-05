import discord
from discord import app_commands
import logging
import traceback

from .. import vesta_client, session, lang
from ..tables import Guild, select

logger = logging.getLogger(__name__)


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

    r = select(Guild).where(Guild.id == interaction.guild_id)
    guild = session.scalar(r)
    if not guild:
        logger.debug(f"Add guild {interaction.guild_id} to the database")
        guild = Guild(id=interaction.guild_id, name=interaction.guild.name)
        session.add(guild)

    guild.review_channel = channel.id
    session.commit()

    await interaction.response.send_message(lang.get("config_review", interaction.guild), ephemeral=True)


@config_manager.command(description="Set Projets Channel")
@app_commands.describe(channel="The future projects channel")
async def projects(interaction: discord.Interaction, channel: discord.TextChannel):
    logger.debug(f"Command /config projects {channel} used")

    r = select(Guild).where(Guild.id == interaction.guild_id)
    guild = session.scalar(r)
    if not guild:
        logger.debug(f"Add guild {interaction.guild_id} to the database")
        guild = Guild(id=interaction.guild_id, name=interaction.guild.name)
        session.add(guild)

    guild.projects_channel = channel.id
    session.commit()

    await interaction.response.send_message(lang.get("config_projects", interaction.guild), ephemeral=True)


@config_manager.command(name="lang", description="Set Guild Lang")
@app_commands.rename(guild_lang='lang')
@app_commands.describe(guild_lang="The lang for the bot")
@app_commands.choices(guild_lang=[app_commands.Choice(name=l, value=l) for l in lang.data])
async def change_lang(interaction: discord.Interaction, guild_lang: app_commands.Choice[str]):
    logger.debug(f"Command /config lang {guild_lang.value} used")

    r = select(Guild).where(Guild.id == interaction.guild_id)
    guild = session.scalar(r)
    if not guild:
        logger.debug(f"Add guild {interaction.guild_id} to the database")
        guild = Guild(id=interaction.guild_id, name=interaction.guild.name)
        session.add(guild)

    guild.lang = guild_lang.value
    session.commit()

    await interaction.response.send_message(lang.get("config_lang", interaction.guild), ephemeral=True)


vesta_client.tree.add_command(config_manager)
