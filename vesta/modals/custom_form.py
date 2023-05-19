import re
import logging
import traceback

from discord import app_commands
import discord.ui
from sqlalchemy import select

from .. import session_maker, vesta_client, lang_file
from ..tables import User, CustomCommand

logger = logging.getLogger(__name__)
session = session_maker()

url_regex = r'^[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
http_regex = r'^https?:\/\/[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
custom_regex = "^[a-z0-9_-]{1,32}$"


class CustomSlashForm(discord.ui.Modal, title=""):
    command_title = discord.ui.TextInput(
        label="",
        style=discord.TextStyle.short,
        max_length=100
    )
    command_content = discord.ui.TextInput(
        label="",
        style=discord.TextStyle.long,
    )
    command_url = discord.ui.TextInput(
        label="",
        style=discord.TextStyle.short,
        required=False,
        max_length=511
    )
    command_image = discord.ui.TextInput(
        label="",
        style=discord.TextStyle.short,
        required=False,
        max_length=511
    )
    command_colour = discord.ui.TextInput(
        label="",
        style=discord.TextStyle.short,
        placeholder="fdfd58",
        required=False,
        max_length=6,
        min_length=6
    )

    def __init__(self, keyword, interaction):
        logger.debug(f"CustomSlashForm created for {interaction.user}")

        self.title = lang_file.get("custom_form", interaction.guild)
        self.command_title.label = lang_file.get("custom_form_title", interaction.guild)
        self.command_content.label = lang_file.get("custom_form_content", interaction.guild)
        self.command_url.label = lang_file.get("custom_form_link", interaction.guild)
        self.command_image.label = lang_file.get("custom_form_image", interaction.guild)
        self.command_colour.label = lang_file.get("custom_form_color", interaction.guild)

        super().__init__()
        self.keyword = keyword

    async def on_submit(self, interaction: discord.Interaction):
        logger.debug(f"CustomSlashForm submitted for {interaction.user}")

        command_title = self.command_title.value.strip()
        command_content = self.command_content.value.strip()
        if not command_title or not command_content:
            return await interaction.response.send_message(lang_file.get("custom_invalid_args", interaction.guild), ephemeral=True)

        command_url = self.command_url.value
        if command_url and not re.match(http_regex, command_url):
            if re.match(url_regex, command_url):
                command_url = 'https://' + command_url
            else:
                return await interaction.response.send_message(
                    content=lang_file.get("invalid_link", interaction.guild),
                    ephemeral=True,
                )
        image_url = self.command_image.value
        if image_url and not re.match(http_regex, image_url):
            if re.match(url_regex, image_url):
                image_url = 'https://' + image_url
            else:
                return await interaction.response.send_message(
                    content=lang_file.get("invalid_image_link", interaction.guild),
                    ephemeral=True,
                )
        r = select(User).where(User.id == interaction.user.id)
        author = session.scalar(r)
        if not author:
            author = User(
                id=interaction.user.id,
                name=interaction.user.display_name,
                avatar_url=interaction.user.display_avatar.url.split("?")[0]
            )
            session.add(author)

        custom_command = CustomCommand(
            guild_id=interaction.guild_id,
            keyword=self.keyword,
            title=command_title,
            content=command_content,
            source_url=command_url,
            image_url=image_url,
            colour=int(self.command_colour.value, 16) if self.command_colour.value else None,
            author=author
        )
        session.add(custom_command)

        try:
            session.commit()
        except:
            session.rollback()

            logger.error(traceback.format_exc())
            return await interaction.response.send_message(lang_file.get("unexpected_error", interaction.guild),
                                                           ephemeral=True)

        await interaction.response.send_message(lang_file.get("command_created", interaction.guild), ephemeral=True)

        @app_commands.guild_only()
        async def command(interaction: discord.Interaction):
            await interaction.response.send_message(embed=custom_command.embed())

        custom = app_commands.Command(name=self.keyword, description=command_title, callback=command)

        logger.info(f"New Custom Guild {interaction.guild.name} : {custom} name : {custom.name} description : {custom.description} end")

        vesta_client.tree.add_command(custom, guild=interaction.guild)
        await vesta_client.tree.sync(guild=interaction.guild)

    async def on_error(self, interaction, error):
        logger.error(traceback.format_exc())
        await interaction.response.send_message(lang_file.get("unexpected_error", interaction.guild), ephemeral=True)


class CustomMenuForm(discord.ui.Modal, title=""):
    command_keyword = discord.ui.TextInput(
        label="",
        max_length=32
    )
    command_title = discord.ui.TextInput(
        label="",
        style=discord.TextStyle.short,
        max_length=100
    )
    command_url = discord.ui.TextInput(
        label="",
        style=discord.TextStyle.short,
        required=False,
        max_length=511
    )
    command_image = discord.ui.TextInput(
        label="",
        style=discord.TextStyle.short,
        required=False,
        max_length=511
    )
    command_colour = discord.ui.TextInput(
        label="",
        style=discord.TextStyle.short,
        placeholder="fdfd58",
        required=False,
        max_length=6,
        min_length=6
    )

    def __init__(self, content, author, interaction):
        logger.debug(f"CustomMenuForm created for {interaction.user}")

        self.title = lang_file.get("custom_form", interaction.guild)
        self.command_keyword.label = lang_file.get("custom_form_keyword", interaction.guild)
        self.command_title.label = lang_file.get("custom_form_title", interaction.guild)
        self.command_url.label = lang_file.get("custom_form_link", interaction.guild)
        self.command_image.label = lang_file.get("custom_form_image", interaction.guild)
        self.command_colour.label = lang_file.get("custom_form_color", interaction.guild)

        super().__init__()
        self.content = content
        self.author = author

    async def on_submit(self, interaction: discord.Interaction):
        logger.debug(f"CustomMenuForm submitted for {interaction.user}")

        keyword = self.command_keyword.value.lower()
        if not re.match(custom_regex, keyword):
            return await interaction.response.send_message(lang_file.get("invalid_keyword", interaction.guild), ephemeral=True)

        command_title = self.command_title.value.strip()
        if not command_title:
            return await interaction.response.send_message(lang_file.get("custom_invalid_args", interaction.guild), ephemeral=True)

        command_url = self.command_url.value
        if command_url and not re.match(http_regex, command_url):
            if re.match(url_regex, command_url):
                command_url = 'https://' + command_url
            else:
                return await interaction.response.send_message(
                    content=lang_file.get("invalid_link", interaction.guild),
                    ephemeral=True,
                )
        image_url = self.command_image.value
        if image_url and not re.match(http_regex, image_url):
            if re.match(url_regex, image_url):
                image_url = 'https://' + image_url
            else:
                return await interaction.response.send_message(
                    content=lang_file.get("invalid_image_link", interaction.guild),
                    ephemeral=True,
                )
        r = select(User).where(User.id == self.author.id)
        author = session.scalar(r)
        if not author:
            author = User(
                id=self.author.id,
                name=self.author.display_name,
                avatar_url=self.author.display_avatar.url.split("?")[0]
            )
            session.add(author)
        r = select(CustomCommand).where(CustomCommand.guild_id == interaction.guild_id)
        r = r.where(CustomCommand.keyword == keyword)
        if session.scalar(r):
            return await interaction.response.send_message(lang_file.get("command_already_exist", interaction.guild), ephemeral=True)
        custom_command = CustomCommand(
            guild_id=interaction.guild_id,
            keyword=keyword,
            title=command_title,
            content=self.content,
            source_url=command_url,
            image_url=image_url,
            colour=int(self.command_colour.value, 16) if self.command_colour.value else None,
            author=author,
        )
        session.add(custom_command)

        try:
            session.commit()
        except:
            session.rollback()

            logger.error(traceback.format_exc())
            return await interaction.response.send_message(lang_file.get("unexpected_error", interaction.guild),
                                                           ephemeral=True)

        await interaction.response.send_message(lang_file.get("command_created", interaction.guild), ephemeral=True)

        @app_commands.guild_only()
        async def command(interaction: discord.Interaction):
            await interaction.response.send_message(embed=custom_command.embed())

        custom = app_commands.Command(name=keyword, description=command_title, callback=command)

        vesta_client.tree.add_command(custom, guild=interaction.guild)
        await vesta_client.tree.sync(guild=interaction.guild)

    async def on_error(self, interaction, error):
        logger.error(traceback.format_exc())
        await interaction.response.send_message(lang_file.get("unexpected_error", interaction.guild), ephemeral=True)
