import re
import traceback
import discord
from sqlalchemy import select

from .. import vesta_client, session, lang
from ..views import Review
from ..tables import Presentation, User, Guild

url_regex = r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
http_regex = r'https?:\/\/[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'


class PresentationForm(discord.ui.Modal, title=""):
    presentation_title = discord.ui.TextInput(
        label="",
        max_length=255,
    )

    description = discord.ui.TextInput(
        label="",
        style=discord.TextStyle.long,
        min_length=100,
    )

    link = discord.ui.TextInput(
        label="",
        max_length=255
    )

    image_url = discord.ui.TextInput(
        label="",
        required=False,
        max_length=511
    )

    def __init__(self, interaction):
        self.title = lang.get("presentation_form", interaction.guild)
        self.presentation_title.label = lang.get("presentation_form_title", interaction.guild)
        self.description.label = lang.get("presentation_form_description", interaction.guild)
        self.link.label = lang.get("presentation_form_link", interaction.guild)
        self.image_url.label = lang.get("presentation_form_image", interaction.guild)

        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):
        link_value = self.link.value
        if not re.match(http_regex, link_value):
            if re.match(url_regex, link_value):
                link_value = 'https://' + link_value
            else:
                return await interaction.response.send_message(
                    content=lang.get("invalid_link", interaction.guild),
                    ephemeral=True,
                )
        image_url = self.image_url.value
        if image_url and not re.match(http_regex, image_url):
            if re.match(url_regex, image_url):
                image_url = 'https://' + image_url
            else:
                return await interaction.response.send_message(
                    content=lang.get("invalid_image_link", interaction.guild),
                    ephemeral=True,
                )

        r = select(User).where(User.id == interaction.user.id)
        author = session.scalar(r)
        if not author:
            author = User(
                id=interaction.user.id,
                name=interaction.user.display_name,
                avatar_url=interaction.user.display_avatar.url
            )
            session.add(author)

        presentation = Presentation(
            title=self.presentation_title.value,
            description=self.description.value,
            url=link_value,
            image_url=image_url,
            author=author,
        )
        author.presentations.append(presentation)
        session.add(presentation)
        session.commit()

        r = select(Guild).where(Guild.id == interaction.guild_id)
        guild = session.scalar(r)
        if not guild or not guild.review_channel:
            return await interaction.response.send_message(lang.get("review_channel_error", interaction.guild))

        embed = presentation.embed('6666ff')
        view = Review(presentation, interaction)
        channel = vesta_client.get_channel(guild.review_channel)
        if not channel:
            return await interaction.response.send_message(lang.get("review_channel_error", interaction.guild))
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(
            content=lang.get("presentation_sent", interaction.guild),
            ephemeral=True)
        await view.wait()

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(
            content=lang.get("unexpected_error", interaction.guild),
            ephemeral=True,
        )
        traceback.print_exc()

