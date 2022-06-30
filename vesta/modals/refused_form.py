import discord

from .. import vesta_client, lang


class RefusedReasonForm(discord.ui.Modal, title=""):
    reason = discord.ui.TextInput(
        label="",
        style=discord.TextStyle.long
    )

    def __init__(self, presentation, interaction):
        self.title = lang.get("denied_form", interaction.guild)
        self.reason.label = lang.get("denied_form_reason", interaction.guild)
        super().__init__()
        self.presentation = presentation

    async def on_submit(self, interaction: discord.Interaction):
        presentation_embed = self.presentation.embed('222222')
        reason_embed = discord.Embed(
            colour=int('ff2222', 16),
            title=lang.get("denied_feedback_title", interaction.guild),
            description=lang.get("denied_feedback_content", interaction.guild) + f" {self.reason.value}",
        )
        user = await vesta_client.fetch_user(self.presentation.author_id)
        await user.send(embeds=[presentation_embed, reason_embed])
        await interaction.response.send_message(lang.get("denied_registered", interaction.guild), ephemeral=True)
