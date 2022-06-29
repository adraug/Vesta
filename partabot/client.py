import re
import random

import discord
from discord import app_commands

from . import GUILD

regex_name = r"[A-Za-z0-9À-ÿ ]{3}[A-Za-z0-9À-ÿ\/.+=()\[\]{}&%*!:;,?§<>_ -|#]{0,29}"

with open("partabot/names.txt") as file:
    names = file.read().split(", ")

with open("partabot/adjectives.txt") as file:
    adjectives = file.read().split(", ")


class PartaBot(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def setup_hook(self):
        self.tree.copy_global_to(guild=GUILD)
        await self.tree.sync(guild=GUILD)

    async def on_member_join(self, member):
        if not re.match(regex_name, member.display_name):
            await member.edit(nick=f"{random.choice(names).capitalize()}{random.choice(adjectives).capitalize()}")

    async def on_member_update(self, before, after):
        if not re.match(regex_name, after.display_name):
            await after.edit(nick=f"{random.choice(names).capitalize()}{random.choice(adjectives).capitalize()}")
