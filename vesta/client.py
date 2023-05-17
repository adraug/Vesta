import re
import random
import logging

import discord
from discord import app_commands

from . import session_maker
from .tables import CustomCommand, select

logger = logging.getLogger(__name__)

regex_name = r"^[A-Za-z0-9À-ÿ ]{3}[A-Za-z0-9À-ÿ\/.+=()\[\]{}&%*!:;,?§<>_ -|#]{0,29}$"

with open("vesta/data/names.txt") as file:
    names = file.read().split(", ")

with open("vesta/data/adjectives.txt") as file:
    adjectives = file.read().split(", ")


class Vesta(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        logger.info(f"Logged on as {self.user}")

        for com in self.tree.get_commands():
            logger.debug(f"Globals {com} name : {com.name}")

        await self.tree.sync()
        for guild in self.guilds:
            active = False

            r = select(CustomCommand).where(CustomCommand.guild_id == guild.id)
            with session_maker() as session:
                responses = session.scalars(r)
                for custom_command in responses:
                    active = True

                    def create_command(custom_command):
                        @app_commands.guild_only()
                        async def command(interaction: discord.Interaction):
                            await interaction.response.send_message(embed=custom_command.embed())

                        return app_commands.Command(name=custom_command.keyword.lower(), description=custom_command.title,
                                                    callback=command)

                    self.tree.add_command(create_command(custom_command), guild=guild)

            for com in self.tree.get_commands(guild=guild):
                logger.debug(f"Custom {com} name : {com.name} description : {com.description} end")

            if active:
                await self.tree.sync(guild=guild)

    async def on_member_join(self, member: discord.Member):
        logger.debug(f"Member joined : {member}!")
        if not (await member.guild.fetch_member(self.user.id)).guild_permissions.manage_nicknames:
            logger.debug(f"Bot doesn't have manage nicknames permission on {member.guild}")
            return

        if not re.match(regex_name, member.display_name):
            await member.edit(nick=f"{random.choice(names).capitalize()}{random.choice(adjectives).capitalize()}")

    async def on_member_update(self, before: discord.Member, after: discord.Member):
        logger.debug(f"Member update : {after}!")
        if not (await after.guild.fetch_member(self.user.id)).guild_permissions.manage_nicknames:
            logger.debug(f"Bot doesn't have manage nicknames permission on {after.guild}")
            return

        if not after.guild_permissions.manage_nicknames and not re.match(regex_name, after.display_name):
            await after.edit(nick=f"{random.choice(names).capitalize()}{random.choice(adjectives).capitalize()}")

    async def setup_hook(self):
        interaction = type('', (), {})()
        guild = type('', (), {})()
        guild.id = 0
        guild.preferred_locale = "en"
        interaction.guild = guild

        from .views import Review

        self.add_view(Review(interaction))