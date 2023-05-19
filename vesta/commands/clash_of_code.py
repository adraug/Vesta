import logging
import re

import discord
from discord import app_commands
from sqlalchemy import select

from .. import vesta_client, session_maker, lang_file
from ..services import clash_of_code_helper, State
from ..services.clash_of_code_helper import start_update_loop
from ..tables import ClashOfCodeGuildGame
from ..tables import Guild

logger = logging.getLogger(__name__)
session = session_maker()

regex_clash_of_code_game = r"^(https://|)(www.|)codingame.com/clashofcode/clash/[^/]+(/|)$"


@vesta_client.tree.command(name="clash-of-code", description="Invites users with the \"Clash of Code\" role to play")
@app_commands.describe(link="The link to the Clash of Code game")
async def coc(interaction: discord.Interaction, link: str):
    if not re.match(regex_clash_of_code_game, link):
        await _send_error(interaction, "coc_invalid_link")
        return

    game_id = clash_of_code_helper.game_id_from_link(link)
    game = clash_of_code_helper.fetch(game_id)

    if not game:
        await _send_error(interaction, "coc_invalid_link")
        return

    if game.state != State.PENDING:
        await _send_error(interaction, "coc_game_already_started")
        return

    r = select(ClashOfCodeGuildGame).where(ClashOfCodeGuildGame.guild_id == interaction.guild.id)
    guild_game: ClashOfCodeGuildGame = session.scalar(r)

    if guild_game and not guild_game.can_start_new():
        await _send_error(interaction, "coc_already_in_progress")
        return

    if not guild_game:
        logger.debug(f"Creating new guild game for guild {interaction.guild_id}")
        guild_game = ClashOfCodeGuildGame(guild_id=interaction.guild_id)
        session.add(guild_game)

    r = select(Guild).where(Guild.id == interaction.guild_id)
    guild: Guild = session.scalar(r)
    if not guild:
        logger.debug(f"Add guild {interaction.guild_id} to the database")
        guild = Guild(id=interaction.guild_id, name=interaction.guild.name)
        session.add(guild)

    if guild.coc_role is None:
        await _send_error(interaction, "coc_role_not_set")
        return

    role = interaction.guild.get_role(guild.coc_role)
    if role is None:
        await _send_error(interaction, "coc_role_not_found")
        return

    if guild.coc_channel is None:
        await _send_error(interaction, "coc_channel_not_set")
        return

    channel = interaction.guild.get_channel(guild.coc_channel)
    if channel is None:
        await _send_error(interaction, "coc_channel_not_found")
        return

    view = discord.ui.View()
    view.add_item(discord.ui.Button(
        label=lang_file.get("coc_game_join", interaction.guild),
        url=game.link,
        emoji="🎮"
    ))

    embed = game.embed(lang_file, interaction.guild)
    embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)

    announcement_message = await channel.send(
        content=f"{role.mention} {lang_file.get('coc_game_invite', interaction.guild)}",
        embed=embed,
        view=view
    )

    guild_game.last_clash_id = game_id
    guild_game.announcement_message_id = announcement_message.id
    session.commit()

    await interaction.response.send_message(
        lang_file.get("coc_successfully_invited", interaction.guild),
        ephemeral=True
    )

    start_update_loop(message=announcement_message, guild=interaction.guild)


async def _send_error(interaction: discord.Interaction, key: str):
    await interaction.response.send_message(
        "❌ " + lang_file.get(key, interaction.guild),
        ephemeral=True
    )
