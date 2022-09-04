from datetime import datetime
import discord
import logging
import traceback

from .. import session_maker, vesta_client, lang
from ..modals import RefusedReasonForm
from ..tables import select, Guild, Presentation

logger = logging.getLogger(__name__)
session = session_maker()


class DropdownReview(discord.ui.Select):
    def __init__(self, interaction):
        options = [
            discord.SelectOption(label=lang.get("reason_not_enough_code", interaction.guild), value="text_not_enough_code", description='', emoji='📝'),
            discord.SelectOption(label=lang.get("reason_not_open_source", interaction.guild), value="text_not_open_source", description='', emoji='🔒'),
            discord.SelectOption(label=lang.get("reason_illegal", interaction.guild), value="text_illegal", description='', emoji='👮'),
            discord.SelectOption(label=lang.get("reason_other", interaction.guild), value="Other", description='', emoji='✒')
        ]
        super().__init__(placeholder=lang.get("deny", interaction.guild), options=options, custom_id="deny_select")

    async def callback(self, interaction: discord.Interaction):

        r = select(Presentation).where(Presentation.message_id == interaction.message.id)
        presentation = session.scalar(r)

        logger.debug(f"Presentation {presentation.id} : Denied")

        if self.values[0] == 'Other':
            await interaction.response.send_modal(RefusedReasonForm(presentation, interaction))
        else:
            presentation_embed = presentation.embed('222222')
            reason_embed = discord.Embed(
                colour=int('ff2222', 16),
                title=lang.get("denied_feedback_title", interaction.guild),
                description=f"{lang.get('denied_feedback_content', interaction.guild)} {lang.get(self.values[0], interaction.guild)}")
            user = await vesta_client.fetch_user(presentation.author_id)
            await user.send(embeds=[presentation_embed, reason_embed])

        presentation.reviewed = True
        presentation.review_date = datetime.now()
        presentation.accepted = False
        presentation.reviewed_by = interaction.user.id

        try:
            session.commit()
        except:
            session.rollback()

            logger.error(traceback.format_exc())
            return await interaction.response.send_message(lang.get("unexpected_error", interaction.guild),
                                                           ephemeral=True)

        embed = interaction.message.embeds[0]
        embed.colour = int("ff2222", 16)
        embed.set_footer(text=lang.get("denied_by", interaction.guild) + f" {interaction.user.display_name}")
        embed.timestamp = presentation.review_date
        await interaction.message.edit(embed=embed, view=None)
        self.view.stop()


class AcceptReview(discord.ui.Button):

    def __init__(self, interaction):
        super().__init__(style=discord.ButtonStyle.green, label=lang.get("accept", interaction.guild), custom_id="accept_button")

    async def callback(self, interaction: discord.Interaction):

        r = select(Presentation).where(Presentation.message_id == interaction.message.id)
        presentation = session.scalar(r)

        logger.debug(f"Presentation {presentation.id} : Accepted")

        r = select(Guild).where(Guild.id == interaction.guild_id)
        guild = session.scalar(r)

        if not guild or not guild.projects_channel:
            return interaction.response.send_message(lang.get("projects_channel_error", interaction.guild))

        channel = vesta_client.get_channel(guild.projects_channel)
        if not channel:
            return interaction.response.send_message(lang.get("projects_channel_error", interaction.guild))

        presentation.reviewed = True
        presentation.review_date = datetime.now()
        presentation.accepted = True
        presentation.reviewed_by = interaction.user.id

        try:
            session.commit()
        except:
            session.rollback()

            logger.error(traceback.format_exc())
            return await interaction.response.send_message(lang.get("unexpected_error", interaction.guild),
                                                           ephemeral=True)

        embed = interaction.message.embeds[0]
        embed.colour = int("22ff22", 16)
        embed.set_footer(text=lang.get("accepted_by", interaction.guild) + f" {interaction.user.display_name}")
        embed.timestamp = presentation.review_date
        await interaction.response.edit_message(embed=embed, view=None)
        embed.title = " ".join(embed.title.split()[1:])

        message = await channel.send(embed=embed)
        await message.create_thread(name=lang.get("thread_project", interaction.guild) + " [" + embed.title + "]")

        self.view.stop()


class Review(discord.ui.View):

    def __init__(self, interaction):
        super().__init__(timeout=None)
        self.add_item(AcceptReview(interaction))
        self.add_item(DropdownReview(interaction))

