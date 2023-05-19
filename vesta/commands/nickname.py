import re
from typing import Optional
import logging
import traceback

import discord
from discord import app_commands

from .. import vesta_client, session_maker, lang_file
from ..tables import select, Ban

logger = logging.getLogger(__name__)
session = session_maker()

regex_name = r"^[A-Za-z0-9À-ÿ ]{3}[A-Za-z0-9À-ÿ\/.+=()\[\]{}&%*!:;,?§<>_ -|#]{0,29}$"


@vesta_client.tree.command(description="Change your pseudonyme")
@app_commands.guild_only()
@app_commands.describe(name="Your future username")
@app_commands.checks.bot_has_permissions(manage_nicknames=True)
async def nickname(interaction: discord.Interaction, name: str):
    logger.debug(f"Command /nickname {name} used")

    r = select(Ban).where(Ban.user_id == interaction.user.id).where(Ban.guild_id == interaction.guild.id)
    response = session.scalar(r)
    if response and response.nickname_banned:
        return await interaction.response.send_message(
            lang_file.get("nickname_banned", interaction.guild),
            ephemeral=True)

    if not interaction.user.guild_permissions.manage_nicknames and not re.match(regex_name, name):
        response_embed = discord.Embed(color=int("FF4444", 16), title=lang_file.get("nickname_incorrect_title", interaction.guild),
                                       description=lang_file.get("nickname_incorrect_description", interaction.guild) + f"`{regex_name}`")
        return await interaction.response.send_message(embed=response_embed, ephemeral=True)

    if len(name) > 32:
        return await interaction.response.send_message(lang_file.get("nick_too_long", interaction.guild), ephemeral=True)

    await interaction.user.edit(nick=name)
    await interaction.response.send_message(
        content=lang_file.get("nickname_changed", interaction.guild), ephemeral=True)


@nickname.error
async def nickname_error(interaction: discord.Interaction, error):
    logger.debug(f"Error {error} raised")
    if isinstance(error, app_commands.errors.BotMissingPermissions):
        await interaction.response.send_message(
            lang_file.get("bot_permissions_error", interaction.guild) + f" {', '.join(error.missing_permissions)}",
            ephemeral=True)
    else:
        logger.error(traceback.format_exc())
        await interaction.response.send_message(lang_file.get("unexpected_error", interaction.guild), ephemeral=True)


@app_commands.guild_only()
@app_commands.default_permissions(manage_nicknames=True)
class NickManage(app_commands.Group, name="nickmanage", description="Nickname manager"):

    async def on_error(self, interaction: discord.Interaction, error):
        logger.debug(f"Error {error} raised")
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                lang_file.get("permissions_error", interaction.guild), ephemeral=True)
        elif isinstance(error, app_commands.errors.BotMissingPermissions):
            await interaction.response.send_message(
                lang_file.get("bot_permissions_error", interaction.guild) + f" {', '.join(error.missing_permissions)}",
                ephemeral=True)
        else:
            logger.error(traceback.format_exc())
            await interaction.response.send_message(lang_file.get("unexpected_error", interaction.guild), ephemeral=True)


nick_manage = NickManage()


@nick_manage.command(description="Ban a user from using the nickname command")
@app_commands.describe(user="The user to ban")
async def ban(interaction: discord.Interaction, user: discord.Member):
    logger.debug(f"Command /nickmanage ban {user} used")

    r = select(Ban).where(Ban.user_id == user.id).where(Ban.guild_id == interaction.guild.id)
    response = session.scalar(r)
    if not response:
        response = Ban(
            user_id=user.id,
            guild_id=interaction.guild.id
        )
        session.add(response)
    response.nickname_banned = True

    try:
        session.commit()
    except:
        session.rollback()

        logger.error(traceback.format_exc())
        return await interaction.response.send_message(lang_file.get("unexpected_error", interaction.guild), ephemeral=True)

    await interaction.response.send_message(
        content=f"{user} " + lang_file.get("nickname_ban", interaction.guild))


@nick_manage.command(description="Unban a user from using the nickname command")
@app_commands.describe(user="The user to unban")
async def unban(interaction: discord.Interaction, user: discord.Member):
    logger.debug(f"Command /nickmanage unban {user} used")

    r = select(Ban).where(Ban.user_id == user.id).where(Ban.guild_id == interaction.guild.id)
    response = session.scalar(r)
    if not (response and response.nickname_banned):
        return await interaction.response.send_message(
            content=f"{user} " + lang_file.get("nickname_not_banned", interaction.guild))
    response.nickname_banned = False

    try:
        session.commit()
    except:
        session.rollback()

        logger.error(traceback.format_exc())
        return await interaction.response.send_message(lang_file.get("unexpected_error", interaction.guild), ephemeral=True)

    await interaction.response.send_message(
        content=f"{user} " + lang_file.get("nickname_unban", interaction.guild))


@nick_manage.command(name="list", description="Show the banlist")
@app_commands.describe(page="The page")
async def banlist(interaction: discord.Interaction, page: Optional[int] = 0):
    logger.debug(f"Command /nickmanage list used")

    r = select(Ban).where(Ban.guild_id == interaction.guild.id)
    r = r.where(Ban.nickname_banned == True).offset(50 * page).limit(50)
    responses = session.scalars(r)

    ban_list = ""
    for response in responses:
        ban_list += f"<@{response.user_id}>\n"

    banned_embed = discord.Embed(title=lang_file.get("nickname_list_title", interaction.guild), description=ban_list)
    banned_embed.set_footer(text=lang_file.get("list_page", interaction.guild) + f" {page}")

    await interaction.response.send_message(embed=banned_embed,
                                            allowed_mentions=discord.AllowedMentions().none())


vesta_client.tree.add_command(nick_manage)
