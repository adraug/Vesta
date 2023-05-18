import logging
import re

import discord
from discord import app_commands

from .. import vesta_client, session_maker, lang

logger = logging.getLogger(__name__)
session = session_maker()

regex_clash_of_code_game = r"^(https://|)(www.|)codingame.com/clashofcode/clash/[^/]+(/|)$"

@vesta_client.tree.command(name="clash-of-code", description="Invites users with the \"Clash of Code\" role to play")
@app_commands.describe(link="The link to the Clash of Code game")
async def coc(interaction: discord.Interaction, link: str):
    if not re.match(regex_clash_of_code_game, link):
        await interaction.response.send_message(
            lang.get("invalid_clash_of_code_link", interaction.guild),
            ephemeral=True
        )

    


    await interaction.response.send_message(f"Acknowledged: {link}!", ephemeral=True)