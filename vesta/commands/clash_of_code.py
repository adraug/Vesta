import logging
import re
import traceback
from typing import Tuple, Optional

import discord
from discord import app_commands
from sqlalchemy import select

from .. import vesta_client, session_maker, lang_file
from ..services import clash_of_code_helper
from ..tables import Guild
from ..tables import ClashOfCodeGuildGame

logger = logging.getLogger(__name__)
session = session_maker()

regex_clash_of_code_game = r"^(https://|)(www.|)codingame.com/clashofcode/clash/[^/]+(/|)$"

@vesta_client.tree.command(name="clash-of-code", description="Invites users with the \"Clash of Code\" role to play")
@app_commands.describe(link="The link to the Clash of Code game")
async def coc(interaction: discord.Interaction, link: str):
    if not re.match(regex_clash_of_code_game, link):
        await interaction.response.send_message(
            lang_file.get("coc_invalid_link", interaction.guild),
            ephemeral=True
        )
        return

    game_id = clash_of_code_helper.game_id_from_link(link)

    game = clash_of_code_helper.fetch(game_id)
    if not game:
        await interaction.response.send_message(
            lang_file.get("coc_invalid_link", interaction.guild),
            ephemeral=True
        )
        return

    if game.started or game.finished:
        await interaction.response.send_message(
            lang_file.get("coc_game_already_started", interaction.guild),
            ephemeral=True
        )
        return

    r = select(ClashOfCodeGuildGame).where(Guild.id == interaction.guild_id)
    guild_game: ClashOfCodeGuildGame = session.scalar(r)

    if guild_game and not guild_game.can_start_new():
        await interaction.response.send_message(
            lang.get("clash_of_code.already_in_progress", interaction.guild),
            ephemeral=True
        )
        return

    if not guild_game:
        logger.debug(f"Creating new guild game for guild {interaction.guild_id}")
        guild_game = ClashOfCodeGuildGame(guild_id=interaction.guild_id)
        session.add(guild_game)

    # (ok, guild, role, channel) = await run_checks_for(interaction)
    # if not ok: return

    r = select(Guild).where(Guild.id == interaction.guild_id)
    guild: Guild = session.scalar(r)

    if guild.coc_role is None:
        await interaction.response.send_message(
            lang_file.get("coc_role_not_set", interaction.guild),
            ephemeral=True
        )
        return

    role = interaction.guild.get_role(guild.coc_role)
    if role is None:
        await interaction.response.send_message(
            lang_file.get("coc_role_not_found", interaction.guild),
            ephemeral=True
        )
        return

    if guild.coc_channel is None:
        await interaction.response.send_message(
            lang_file.get("coc_channel_not_set", interaction.guild),
            ephemeral=True
        )
        return

    channel = interaction.guild.get_channel(guild.coc_channel)
    if channel is None:
        await interaction.response.send_message(
            lang_file.get("coc_channel_not_found", interaction.guild),
            ephemeral=True
        )
        return

    view = discord.ui.View()
    view.add_item(discord.ui.Button(
        label=lang_file.get("coc_game_join", interaction.guild),
        url=game.link,
        emoji="🎮"
    ))

    await channel.send(
        content=f"{role.mention} {lang_file.get('coc_game_invite', interaction.guild)}",
        embed=game.embed(lang_file, interaction.guild),
        view=view
    )

    guild_game.last_clash_id = game_id

    try:
        session.commit()
    except:
        session.rollback()

        logger.error(traceback.format_exc())
        return await interaction.response.send_message(lang_file.get("unexpected_error", interaction.guild), ephemeral=True)
    pass


    await interaction.response.send_message(
        lang_file.get("coc_successfully_invited", interaction.guild),
        ephemeral=True
    )

