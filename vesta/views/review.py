from datetime import datetime

import discord
from .. import session, vesta_client, lang
from ..modals import RefusedReasonForm
from ..tables import select, Guild


class DropdownReview(discord.ui.Select):
    def __init__(self, interaction):
        options = [
            discord.SelectOption(label=lang.get("reason_not_enough_code", interaction.guild), value="text_not_enough_code", description='', emoji='📝'),
            discord.SelectOption(label=lang.get("reason_not_open_source", interaction.guild), value="text_not_open_source", description='', emoji='🔒'),
            discord.SelectOption(label=lang.get("reason_illegal", interaction.guild), value="text_illegal", description='', emoji='👮'),
            discord.SelectOption(label=lang.get("reason_other", interaction.guild), value="Other", description='', emoji='✒')
        ]
        super().__init__(placeholder=lang.get("deny", interaction.guild), options=options)

    async def callback(self, interaction: discord.Interaction):
        print(self.view.presentation.id, ": Denied")
        if self.values[0] == 'Other':
            await interaction.response.send_modal(RefusedReasonForm(self.view.presentation, interaction))
        else:
            presentation_embed = self.view.presentation.embed('222222')
            reason_embed = discord.Embed(
                colour=int('ff2222', 16),
                title=lang.get("denied_feedback_title", interaction.guild),
                description=f"{lang.get('denied_feedback_content', interaction.guild)} {lang.get(self.values[0], interaction.guild)}")
            user = await vesta_client.fetch_user(self.view.presentation.author_id)
            await user.send(embeds=[presentation_embed, reason_embed])
        self.view.presentation.reviewed = True
        self.view.presentation.review_date = datetime.now()
        self.view.presentation.accepted = False
        self.view.presentation.reviewed_by = interaction.user.id
        session.commit()
        embed = interaction.message.embeds[0]
        embed.colour = int("ff2222", 16)
        embed.set_footer(text=lang.get("denied_by", interaction.guild) + f" {interaction.user.display_name}")
        embed.timestamp = self.view.presentation.review_date
        await interaction.message.edit(embed=embed, view=None)
        self.view.stop()


class AcceptReview(discord.ui.Button):

    def __init__(self, interaction):
        super().__init__(style=discord.ButtonStyle.green, label=lang.get("accept", interaction.guild))

    async def callback(self, interaction: discord.Interaction):
        print(self.view.presentation.id, ": Accepted")

        r = select(Guild).where(Guild.id == interaction.guild_id)
        guild = session.scalar(r)

        if not guild or not guild.projects_channel:
            return interaction.response.send_message(lang.get("projects_channel_error", interaction.guild))

        self.view.presentation.reviewed = True
        self.view.presentation.review_date = datetime.now()
        self.view.presentation.accepted = True
        self.view.presentation.reviewed_by = interaction.user.id
        session.commit()
        embed = interaction.message.embeds[0]
        embed.colour = int("22ff22", 16)
        embed.set_footer(text=lang.get("accepted_by", interaction.guild) + f" {interaction.user.display_name}")
        embed.timestamp = self.view.presentation.review_date
        await interaction.response.edit_message(embàed=embed, view=None)
        embed.title = " ".join(embed.title.split()[1:])
        channel = vesta_client.get_channel(guild.projects_channel)
        if not channel:
            return interaction.response.send_message(lang.get("projects_channel_error", interaction.guild))
        await channel.send(embed=embed)
        self.view.stop()


class Review(discord.ui.View):

    def __init__(self, presentation, interaction):
        self.presentation = presentation
        super().__init__()
        self.add_item(AcceptReview(interaction))
        self.add_item(DropdownReview(interaction))

