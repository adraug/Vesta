import logging
import re
from typing import Tuple, Optional

import discord
from discord import app_commands
from sqlalchemy import select

from .. import vesta_client, session_maker, lang
from ..services.clash_of_code_helper import ClashOfCodeHelper, game_id_from_link
from ..tables import Guild
from ..tables.clash_of_code import ClashOfCodeGuildGame

logger = logging.getLogger(__name__)
session = session_maker()

regex_clash_of_code_game = r"^(https://|)(www.|)codingame.com/clashofcode/clash/[^/]+(/|)$"


@vesta_client.tree.command(name="clash-of-code", description="Invites users with the \"Clash of Code\" role to play")
@app_commands.describe(link="The link to the Clash of Code game")
async def coc(interaction: discord.Interaction, link: str):
    if not re.match(regex_clash_of_code_game, link):
        await interaction.response.send_message(
            lang.get("clash_of_code.invalid_link", interaction.guild),
            ephemeral=True
        )
        return

    helper = ClashOfCodeHelper()
    game_id = game_id_from_link(link)

    game = helper.fetch(game_id)
    if not game:
        await interaction.response.send_message(
            lang.get("clash_of_code.invalid_link", interaction.guild),
            ephemeral=True
        )
        return

    if game.started or game.finished:
        await interaction.response.send_message(
            lang.get("clash_of_code.game_already_started", interaction.guild),
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
        guild_game = ClashOfCodeGuildGame(guild_id=interaction.guild_id)
        session.add(guild_game)

    # (ok, guild, role, channel) = await run_checks_for(interaction)
    # if not ok: return

    r = select(Guild).where(Guild.id == interaction.guild_id)
    guild: Guild = session.scalar(r)

    if guild.coc_role is None:
        await interaction.response.send_message(
            lang.get("clash_of_code.role_not_set", interaction.guild),
            ephemeral=True
        )
        return

    role = interaction.guild.get_role(guild.coc_role)
    if role is None:
        await interaction.response.send_message(
            lang.get("clash_of_code.role_not_found", interaction.guild),
            ephemeral=True
        )
        return

    if guild.coc_channel is None:
        await interaction.response.send_message(
            lang.get("clash_of_code.channel_not_set", interaction.guild),
            ephemeral=True
        )
        return

    channel = interaction.guild.get_channel(guild.coc_channel)
    if channel is None:
        await interaction.response.send_message(
            lang.get("clash_of_code.channel_not_found", interaction.guild),
            ephemeral=True
        )
        return

    view = discord.ui.View()
    view.add_item(discord.ui.Button(
        label=lang.get("clash_of_code.game_join"),
        url=game.link,
        emoji="🎮"
    ))

    await channel.send(
        content=f"{role.mention} {lang.get('clash_of_code.game_invite')}",
        embed=game.embed(),
        view=view
    )

    guild_game.game_id = game_id
    session.commit()

    await interaction.response.send_message(
        lang.get("clash_of_code.successfully_invited", interaction.guild),
        ephemeral=True
    )

