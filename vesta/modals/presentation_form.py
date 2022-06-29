import re
import traceback
import discord
from sqlalchemy import select

from .. import partabot_client, REVIEW_CHANNEL, session
from ..views import Review
from ..tables import Presentation, User

url_regex = r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
http_regex = r'https?:\/\/[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'


class PresentationForm(discord.ui.Modal, title="Présentation"):
    presentation_title = discord.ui.TextInput(
        label="Nom du projet",
        max_length=255,
    )

    description = discord.ui.TextInput(
        label="Description du projet",
        style=discord.TextStyle.long,
        min_length=100,
    )

    link = discord.ui.TextInput(
        label="Lien du projet",
        max_length=255
    )

    image_url = discord.ui.TextInput(
        label="Lien de l'image",
        required=False,
        max_length=511
    )

    async def on_submit(self, interaction: discord.Interaction):
        link_value = self.link.value
        if not re.match(http_regex, link_value):
            if re.match(url_regex, link_value):
                link_value = 'https://' + link_value
            else:
                return await interaction.response.send_message(
                    content="Le lien de votre projet n'est pas valide",
                    ephemeral=True,
                )
        image_url = self.image_url.value
        if image_url and not re.match(http_regex, image_url):
            if re.match(url_regex, image_url):
                image_url = 'https://' + image_url
            else:
                return await interaction.response.send_message(
                    content="Le lien de votre image n'est pas valide",
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

        await interaction.response.send_message(
            content='Votre projet sera étudié dans les plus brefs délais',
            ephemeral=True,
        )
        embed = presentation.embed('6666ff')
        view = Review(presentation)
        await partabot_client.get_channel(REVIEW_CHANNEL).send(embed=embed, view=view)
        await view.wait()

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(
            content="Votre demande n'as pas pu aboutir, reessayez plus tard !",
            ephemeral=True,
        )
        traceback.print_exc()

