import asyncio
import logging
import uuid
from typing import Optional

import discord
import requests
from sqlalchemy import select

from . import ClashOfCodeGame, State

BASE_ENDPOINT = "https://www.codingame.com/services/ClashOfCode"
logger = logging.getLogger(__name__)

def game_id_from_link(link: str) -> str:
    return link.split("/")[-1]

def fetch(game_id) -> Optional[ClashOfCodeGame]:
    """
    Retrieves a game object from the API

    :param game_id: The game id to retrieve
    :return: The game object if it exists, None otherwise
    """
    r = requests.post(f"{BASE_ENDPOINT}/findClashByHandle", json=[
        game_id
    ])

    if r.status_code != 200:
        return None

    return ClashOfCodeGame(**r.json())

def update(game: ClashOfCodeGame) -> ClashOfCodeGame:
    """
    Updates the game object with the latest information from the API

    :param game: The game object to update
    :return: The updated game object for chaining convenience
    :raises NameError: If there was an error updating the game object
    """
    r = requests.post(f"{BASE_ENDPOINT}/findClashByHandle", json=[
        game.id
    ])

    if r.status_code != 200:
        raise NameError("There was an error updating the game object")

    game.hydrate(**r.json())
    return game

def resume_update_loops() -> None:
    """
    Resumes all update loops for all guilds

    :return: Nothing
    """
    from .. import session_maker, vesta_client
    from ..tables import ClashOfCodeGuildGame, Guild
    session = session_maker()

    logger.debug(f"Resuming update loops for all guilds")

    r = select(ClashOfCodeGuildGame)
    guild_games: list[ClashOfCodeGuildGame] = session.execute(r).scalars().all()

    for guild_game in guild_games:
        guild = vesta_client.get_guild(guild_game.guild_id)

        if not guild:
            continue

        r = select(Guild).where(Guild.id == guild.id)
        guild_table: Guild = session.scalar(r)

        if not guild_table:
            continue

        announcement_channel = guild.get_channel(guild_table.coc_channel)
        if not announcement_channel:
            continue

        message = announcement_channel.get_partial_message(guild_game.announcement_message_id)
        if not message:
            continue

        start_update_loop(message, guild)

def start_update_loop(message: discord.Message, guild: discord.Guild) -> None:
    """
    Starts an update loop for the given message and guild to
    always match the latest information from the API and the
    message content

    :param message: The message to update
    :param guild: The guild to update the data for
    :return: Nothing
    """
    from .. import session_maker, lang_file
    from ..tables import ClashOfCodeGuildGame
    session = session_maker()

    uid = str(uuid.uuid4())[0:5]

    logger.debug(f"[{uid}] Starting update loop for {message.id} in {guild.id}")

    r = select(ClashOfCodeGuildGame).where(ClashOfCodeGuildGame.guild_id == guild.id)
    guild_game: ClashOfCodeGuildGame = session.scalar(r)
    fetched_game: ClashOfCodeGame = guild_game.fetch()

    # Start a cron that runs every 15 seconds asynchronously
    # This will update the message with the latest information
    # about the game
    async def update_loop(game: ClashOfCodeGame):
        while True:
            game = update(game)
            await message.edit(embed=game.embed(lang_file, guild))

            if game.state == State.FINISHED:
                logger.debug(f"[{uid}] Game {game.id} has finished, deleting from database")

                session.delete(guild_game)
                session.commit()
                break

            await asyncio.sleep(10)

    asyncio.create_task(update_loop(fetched_game))