import discord

from .. import partabot_client


class RefusedReasonForm(discord.ui.Modal, title="Raison de refus"):
    reason = discord.ui.TextInput(
        label="Raison du refus",
        style=discord.TextStyle.long
    )

    def __init__(self, presentation):
        super().__init__()
        self.presentation = presentation

    async def on_submit(self, interaction: discord.Interaction):
        presentation_embed = self.presentation.embed('222222')
        reason_embed = discord.Embed(
            colour=int('ff2222', 16),
            title="Refus de votre présentation",
            description=f"Raison : {self.reason.value}",
        )
        user = await partabot_client.fetch_user(self.presentation.author_id)
        await user.send(embeds=[presentation_embed, reason_embed])
        await interaction.response.send_message('Refus enregistré', ephemeral=True)
