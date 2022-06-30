import re
import random

import discord
from discord import app_commands

from . import session
from .tables import CustomCommand, select

regex_name = r"[A-Za-z0-9À-ÿ ]{3}[A-Za-z0-9À-ÿ\/.+=()\[\]{}&%*!:;,?§<>_ -|#]{0,29}"

with open("vesta/data/names.txt") as file:
    names = file.read().split(", ")

with open("vesta/data/adjectives.txt") as file:
    adjectives = file.read().split(", ")

class Vesta(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        for guild in self.guilds:
            active = False

            r = select(CustomCommand).where(CustomCommand.guild_id == guild.id)
            for custom_command in session.scalars(r):
                active = True
                print(custom_command)

                def create_command(custom_command):
                    @app_commands.guild_only()
                    async def command(interaction: discord.Interaction):
                        await interaction.response.send_message(embed=custom_command.embed())

                    return app_commands.Command(name=custom_command.keyword, description=custom_command.content,
                                                callback=command)

                self.tree.add_command(create_command(custom_command), guild=guild)

            if active:
                await self.tree.sync(guild=guild)

    async def on_member_join(self, member):
        if not re.match(regex_name, member.display_name):
            await member.edit(nick=f"{random.choice(names).capitalize()}{random.choice(adjectives).capitalize()}")

    async def on_member_update(self, before, after):
        if not re.match(regex_name, after.display_name):
            await after.edit(nick=f"{random.choice(names).capitalize()}{random.choice(adjectives).capitalize()}")
