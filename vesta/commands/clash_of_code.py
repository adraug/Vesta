import logging
import re

import discord
from apscheduler.triggers.interval import IntervalTrigger
from discord import app_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from .. import vesta_client, session_maker, lang_file
from ..services import clash_of_code_helper
from ..tables import ClashOfCodeGuildGame
from ..tables import Guild

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

    r = select(ClashOfCodeGuildGame).where(ClashOfCodeGuildGame.guild_id == interaction.guild.id)
    guild_game: ClashOfCodeGuildGame = session.scalar(r)

    if guild_game and not guild_game.can_start_new():
        await interaction.response.send_message(
            lang_file.get("coc_already_in_progress", interaction.guild),
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
    if not guild:
        logger.debug(f"Add guild {interaction.guild_id} to the database")
        guild = Guild(id=interaction.guild_id, name=interaction.guild.name)
        session.add(guild)

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

    embed = game.embed(lang_file, interaction.guild)
    embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)

    announcement_message = await channel.send(
        content=f"{role.mention} {lang_file.get('coc_game_invite', interaction.guild)}",
        embed=embed,
        view=view
    )

    guild_game.last_clash_id = game_id
    guild_game.start_new(game_id, announcement_message.id)

    await interaction.response.send_message(
        lang_file.get("coc_successfully_invited", interaction.guild),
        ephemeral=True
    )

    async def edit():
        logger.debug(f"Editing announcement message for guild {interaction.guild_id}")

        clash_of_code_helper.update(game)

        edited_embed = game.embed(lang_file, interaction.guild)
        edited_embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)

        await announcement_message.edit(
            content=f"{role.mention} {lang_file.get('coc_game_invite', interaction.guild)}",
            embed=edited_embed,
            view=view
        )

        if game.finished:
            return schedule.CancelJob

        scheduler = AsyncIOScheduler()
        scheduler.add_job(edit, trigger=IntervalTrigger(seconds=30))
        scheduler.start()