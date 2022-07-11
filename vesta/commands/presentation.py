import discord
from discord import app_commands
import logging
import traceback

from typing import Optional

from .. import vesta_client, session_maker, lang
from ..modals import PresentationForm
from ..tables import Presentation, select, or_, Guild, Ban

logger = logging.getLogger(__name__)
session = session_maker()


@app_commands.guild_only()
@vesta_client.tree.command(description="Submit a presentation")
async def presentation(interaction: discord.Interaction):
    logger.debug(f"Command /presentation used")

    r = select(Guild).where(Guild.id == interaction.guild_id)
    guild = session.scalar(r)
    if not guild or not guild.review_channel or not guild.projects_channel:
        return await interaction.response.send_message(
            lang.get("presentations_not_available", interaction.guild), ephemeral=True)

    r = select(Ban).where(Ban.user_id == interaction.user.id).where(Ban.guild_id == interaction.guild.id)
    response = session.scalar(r)
    if response and response.presentation_banned:
        return await interaction.response.send_message(
            lang.get("presentations_banned", interaction.guild),
            ephemeral=True)
    await interaction.response.send_modal(PresentationForm(interaction))


@app_commands.guild_only()
@app_commands.default_permissions(ban_members=True)
class PresentationManage(app_commands.Group, name="presentationmanage", description="Presentation manager"):

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


presentation_manage = PresentationManage()


@presentation_manage.command(description="Show a presentation")
@app_commands.describe(research="Presentation's Id or Author's Id")
async def show(interaction: discord.Interaction, research: Optional[str] = None, user: Optional[discord.Member] = None):
    logger.debug(f"Command /presentationmanage show [research={research},user={user}] used")
    if not (research or user):
        return await interaction.response.send_message(
            lang.get("minimum_one_parameter", interaction.guild), ephemeral=True)
    if user:
        r = select(Presentation).where(Presentation.author_id == user.id)
    else:
        if not research.isdecimal() or int(research) > 2 ** 63 - 1:
            return await interaction.response.send_message(
                content=lang.get("invalid_number", interaction.guild),
                ephemeral=True)
        r = select(Presentation).where(or_(Presentation.id == research, Presentation.author_id == research))
    presentations = session.scalars(r).all()
    if not len(presentations):
        return await interaction.response.send_message(
            content=lang.get("no_result", interaction.guild),
            ephemeral=True,
        )
    if len(presentations) == 1:
        presentation = presentations[0]
        embed = presentation.embed('222222')
        return await interaction.response.send_message(embed=embed)
    embed = discord.Embed(
        colour=int('222222', 16),
        title=lang.get("user_result_title", interaction.guild)
    )
    for presentation in presentations:
        emoji = '🕑'
        if presentation.reviewed:
            emoji = ['❌', '✅'][presentation.accepted]
        embed.add_field(name=f"{presentation.id} : {emoji}", value=presentation.title)
    return await interaction.response.send_message(embed=embed)


@presentation_manage.command(description="Ban a user from submitting a presentation")
@app_commands.describe(user="The user to ban")
async def ban(interaction: discord.Interaction, user: discord.Member):
    logger.debug(f"Command /presentationmanage ban {user} used")

    r = select(Ban).where(Ban.user_id == interaction.user.id).where(Ban.guild_id == interaction.guild.id)
    response = session.scalar(r)
    if not response:
        response = Ban(
            user_id=user.id,
            guild_id=interaction.guild.id
        )
        session.add(response)
    response.presentation_banned = True
    session.commit()

    await interaction.response.send_message(
        content=f"{user} " + lang.get("user_result_title", interaction.guild))


@presentation_manage.command(description="Unban a user from submitting a presentation")
@app_commands.describe(user="The user to unban")
async def unban(interaction: discord.Interaction, user: discord.Member):
    logger.debug(f"Command /presentationmanage unban {user} used")

    r = select(Ban).where(Ban.user_id == interaction.user.id).where(Ban.guild_id == interaction.guild.id)
    response = session.scalar(r)
    if not (response and response.presentation_banned):
        return await interaction.response.send_message(
            content=f"{user} " + lang.get("presentations_not_banned", interaction.guild))
    response.presentation_banned = False
    session.commit()

    await interaction.response.send_message(
        content=f"{user} " + lang.get("presentations_unban", interaction.guild))


@presentation_manage.command(name="list", description="Show the banlist")
@app_commands.describe(page="The page")
async def banlist(interaction: discord.Interaction, page: Optional[int] = 0):
    logger.debug(f"Command /presentationmanage list used")

    r = select(Ban).where(Ban.guild_id == interaction.guild.id)
    r = r.where(Ban.presentation_banned == True).offset(50 * page).limit(50)
    results = session.scalars(r)

    ban_list = ""
    for result in results:
        ban_list += f"<@{result.user_id}>\n"

    banned_embed = discord.Embed(title=lang.get("presentations_list_title", interaction.guild), description=ban_list)
    banned_embed.set_footer(text=lang.get("list_page", interaction.guild) + f" {page}")

    await interaction.response.send_message(embed=banned_embed,
                                            allowed_mentions=discord.AllowedMentions().none())


vesta_client.tree.add_command(presentation_manage)
