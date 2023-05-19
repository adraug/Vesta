import logging
import re
from typing import Tuple

import discord
from discord import app_commands
from sqlalchemy import select

from .. import vesta_client, session_maker, lang_file
from ..exceptions import CommandRuntimeError
from ..services import clash_of_code_helper, State
from ..services.clash_of_code_helper import start_update_loop
from ..tables import ClashOfCodeGuildGame
from ..tables import Guild

logger = logging.getLogger(__name__)
session = session_maker()

regex_clash_of_code_game = r"^(https://|)(www.|)codingame.com/clashofcode/clash/[^/]+(/|)$"


@vesta_client.tree.command(name="clash-of-code", description="Invites users with the \"Clash of Code\" role to play")
@app_commands.describe(link="The link to the Clash of Code game")
async def clash_of_code(interaction: discord.Interaction, link: str):
    if not re.match(regex_clash_of_code_game, link):
        await _send_error(interaction, "coc_invalid_link")
        return

    try:
        (game, game_id) = _get_game(link)
        guild_game = _get_guild_game(interaction)
        (guild, role, channel) = _get_guild(interaction)
    except CommandRuntimeError as e:
        await _send_error(interaction, e.message)
        return

    view = discord.ui.View()
    view.add_item(discord.ui.Button(
        label=lang_file.get("coc_game_join", interaction.guild),
        url=game.link,
        emoji="🎮"
    ))

    embed = game.embed(interaction.guild)
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


def _get_game(link: str):
    game_id = clash_of_code_helper.game_id_from_link(link)
    game = clash_of_code_helper.fetch(game_id)

    if not game:
        raise CommandRuntimeError("coc_invalid_link")
    if game.state != State.PENDING:
        raise CommandRuntimeError("coc_game_already_started")

    return game, game_id


def _get_guild_game(interaction: discord.Interaction) -> ClashOfCodeGuildGame:
    r = select(ClashOfCodeGuildGame).where(ClashOfCodeGuildGame.guild_id == interaction.guild.id)
    guild_game: ClashOfCodeGuildGame = session.scalar(r)

    if guild_game and not guild_game.can_start_new():
        raise CommandRuntimeError("coc_already_in_progress")

    if not guild_game:
        logger.debug(f"Creating new guild game for guild {interaction.guild_id}")
        guild_game = ClashOfCodeGuildGame(guild_id=interaction.guild_id)
        session.add(guild_game)

    return guild_game


def _get_guild(interaction: discord.Interaction) -> Tuple[Guild, discord.Role, discord.TextChannel]:
    r = select(Guild).where(Guild.id == interaction.guild_id)
    guild: Guild = session.scalar(r)

    if not guild:
        logger.debug(f"Add guild {interaction.guild_id} to the database")
        guild = Guild(id=interaction.guild_id, name=interaction.guild.name)
        session.add(guild)

    return guild, _get_role(guild, interaction), _get_channel(guild, interaction)


def _get_role(guild: Guild, interaction: discord.Interaction) -> discord.Role:
    if not guild.coc_role:
        raise CommandRuntimeError("coc_role_not_set")

    role = interaction.guild.get_role(guild.coc_role)
    if not role:
        raise CommandRuntimeError("coc_role_not_found")

    return role


def _get_channel(guild: Guild, interaction: discord.Interaction) -> discord.TextChannel:
    if not guild.coc_channel:
        raise CommandRuntimeError("coc_channel_not_set")

    channel = interaction.guild.get_channel(guild.coc_channel)
    if not channel:
        raise CommandRuntimeError("coc_channel_not_found")

    return channel


async def _send_error(interaction: discord.Interaction, key: str):
    msg = lang_file.get(key, interaction.guild)
    await interaction.response.send_message(f"❌ {msg}", ephemeral=True)
